# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from models import Image, ImageType, Segment,Tag
from segment.forms import ImageForm,SegmentForm,GenerateImagesForm,ImageTypeForm
from django.contrib.auth.models import User
from settings import BASE_DIR
import os
import PIL
import SimpleCV
import oct2py
import numpy
import traceback
from django.contrib.auth.decorators import login_required
from collections import OrderedDict
import random
import string
import zipfile
import StringIO
from django.db.models import signals





def log(s):
    print s

def home(request):
    p = "/limages/"
    return HttpResponseRedirect(p)


class LImages(ListView):
    model = Image #implies -> queryset = models.Car.objects.all()
    template_name = 'limages.html' #optional (this is the default name)
    context_object_name = "images_by_type" #default is object_list
    paginate_by = 50 #and that's it !!
    base_url= '/limages/'
    view_name = 'LImages'
    header = 'Trainning set'

    def get(self,request):
        self.id_image = ''
        self.request = request
        self.image_types = ImageType.objects.filter(users_shared=request.user).order_by('name')
        images = Image.objects.filter(image_type=self.image_types).order_by('image_type__name')
        images_in_type = []
        type = ''
        group = {}
        for image in images: 
            image_type = ImageType.objects.get(id=image.image_type_id)
            if type != image_type.name:
                if type != '':
                    images_in_type.append(group)
                group = {}
                type = image_type.name
                group = {'image_type':type,'image_type_id':image_type.id,'rows':[]}
            group['rows'].append(image)
        images_in_type.append(group)
        self.queryset = images_in_type
        return super(LImages, self).get(request)
 
    def get_context_data(self, **kwargs):
        context = super(LImages, self).get_context_data(**kwargs)
        context['header'] = self.header
        context['form_image'] = ImageForm(user=self.request.user)
        context['image_types'] = self.image_types
        context['download_tags'] = Tag.objects.all().order_by('name')
        context['average_width'] = 20
        context['average_height'] = 20
        users = User.objects.all().exclude(id=self.request.user.id).order_by('username')
        users_list = []
        for u in users:
            users_list.append(u.username)
        context['users'] = '["'+'","'.join(users_list)+'"]'
        return context

    def post(self,request):
        if 'btn_create_image' in request.POST:
            form_image = ImageForm(user=request.user,data=request.POST,files=request.FILES) 
            if form_image.is_valid():
                form_image.save()
        if 'btn_remove_image' in request.POST:
            id_image = request.POST['selected_row']
            self.delete_image(id_image)
        if 'btn_create_image_type' in request.POST:
            new_image_type = request.POST['name_image_type']
            folder_random_name = get_random_name()
            it = ImageType()
            it.name = new_image_type
            it.user = request.user
            it.folder = folder_random_name
            it.save()
            it.users_shared.add(request.user)
        if 'btn_share_image_type' in request.POST:
            image_type = request.POST['image_type']
            it = ImageType.objects.get(id=image_type)
            username = request.POST['username']
            users = User.objects.filter(username=username)
            if len(users) > 0:
                user = users[0]
                it.users_shared.add(user)
        if 'btn_delete_image_type' in request.POST:
            image_type = request.POST['image_type']
            it = ImageType.objects.get(id=image_type)
            if it.user == request.user:
                images = Image.objects.filter(image_type=it)
                for image in images:
                    segments = Segment.objects.filter(image=image)
                    for segment in segments:
                        segment.delete()
                    self.delete_image(image.id)
                tags = Tag.objects.filter(image_type=it)
                for tag in tags:
                    tag.delete()
                it.delete()
            else:
                it.users_shared.remove(request.user)
        return HttpResponseRedirect('/limages/') 

    def delete_image(self, id_image):
        image = Image.objects.get(id = id_image)
        if image:
            filepath = BASE_DIR+'/segment/static/'+str(image.filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
            image.delete()

def get_random_name():
    name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    image_types = ImageType.objects.filter(folder=name)
    if len(image_types) > 0:
        get_random_name
    return name


class SegmentImage(TemplateView):
    template_name='segment_image.html'
    header = 'Segment Image'

    def get(self,request):
        self.id_image= ''
        self.request = request
        self.zoom = 1
        self.draw_segments = False
        if 'id' in request.GET:
            self.id_image = int(request.GET['id'])
            if 'zoom' in request.GET:
                self.zoom = request.GET['zoom'] or 1
            if 'draw_segments' in request.GET:
                self.draw_segments=request.GET['draw_segments'] in ['True']
        return super(SegmentImage, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(SegmentImage, self).get_context_data(**kwargs)
        context['header'] = self.header
        if self.id_image:
            context['id_image'] = self.id_image
            image = Image.objects.get(id=self.id_image)
            context['download_tags'] = Tag.objects.filter(image_type=image.image_type).order_by('name')
            context['form'] = ImageForm(instance=image,user=self.request.user)
            new_segment = Segment(image=image)
            context['form_segment'] = SegmentForm(instance=new_segment)
            segments = Segment.objects.filter(image_id=self.id_image)
            context['segments'] = segments
            context['form_generate_image'] = GenerateImagesForm(user=self.request.user,image=image)
            context['zoom'] = self.zoom
            context['draw_segments'] = self.draw_segments
            w = h = 0
            for segment in segments:
                w += segment.x2-segment.x1
                h += segment.y2-segment.y1
            size = len(segments)
            if size == 0:
                size = 1
            context['average_width'] = int(w/size)
            context['average_height'] = int(h/size)
            if self.draw_segments:
                tags = Tag.objects.filter(image_type=image.image_type)
                tags = {}
                seg_tags = Tag.objects.filter(image_type=image.image_type)
                for tag in seg_tags:
                    tags[tag.name]=[]
                    for segment in segments:
                        tags_aux = Tag.objects.filter(segment=segment)
                        if tag in tags_aux:
                            tags[tag.name].append(segment)
                tags=OrderedDict(sorted(tags.items(), key=lambda t: t[0]))
                context['tags'] = tags
        return context

    def post(self,request):
        id_image=zoom=''
        if 'image' in request.POST:
            id_image = request.POST['image']
            image = Image.objects.get(id=id_image)
            path_segments = BASE_DIR+'/segment/static/uploads/%s/%s/segments/'%(request.user.id,image.image_type.folder)
            if not os.path.exists(path_segments):
                os.makedirs(path_segments)
            draw_segments='false'
            if 'zoom' in request.POST:
                zoom = float(request.POST['zoom'])
            if 'draw_segments' in request.POST:
                draw_segments = request.POST['draw_segments']
            if 'btn_return' in request.POST:
                return HttpResponseRedirect('/limages/') 
            if 'btn_create_segment' in request.POST:
                post = save_new_tags(request,image)
                form_segment = SegmentForm(post)     
                if form_segment.is_valid():
                    try:   
                        #TODO primer crear imatge i dsp guardar segment, no a l'inreves
                        segment = form_segment.save()   #commit=False  
                        filename = 'segment_'+str(id_image)+"_"+str(segment.id)+'.jpg'
                        segment.filename = 'uploads/%s/%s/segments/%s'%(request.user.id,image.image_type.folder,filename)
                        segment.save() 
                        x1=int(request.POST['x1'])
                        y1=int(request.POST['y1'])
                        x2=int(request.POST['x2'])
                        y2=int(request.POST['y2'])
                        image = Image.objects.get(id=id_image)
                        image_path = BASE_DIR+'/segment/static/'+str(image.filename)
                        i = PIL.Image.open(image_path)
                        filepath_segment = path_segments +filename
                        i.crop((x1,y1,x2,y2)).save(filepath_segment)  
                        segment = form_segment.save()
                    except:
                        traceback.print_exc()
            elif 'btn_generate_images' in request.POST:
                form_generate_images = GenerateImagesForm(user=request.user,image=image,data=request.POST)
                if form_generate_images.is_valid():
                    tags = request.POST['tags']
                    segments = Segment.objects.filter(tags=tags,image_id=id_image)
                    for segment in segments:
                        image = Image()
                        image.name = segment.filename.split('/')[4].split('.jpg')[0]
                        image.filename = segment.filename
                        image.image_type_id = request.POST['image_type']
                        image.parent_segment_id = segment.id
                        image.save()
                    
            elif 'btn_remove_segment' in request.POST:
                id_segment = request.POST['selected_row']
                segment = Segment.objects.get(id = id_segment)
                if segment:
                    filepath = path_segments+'segment_'+str(id_image)+"_"+str(segment.id)+'.jpg'
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                    segment.delete()
            elif 'btn_zoom_in' in request.POST:
                if zoom < 5:
                    zoom = zoom+0.2
                return HttpResponseRedirect('/segment_image/?id='+id_image+'&zoom='+str(zoom)+'&draw_segments='+str(draw_segments))
            elif 'btn_zoom_out' in request.POST:
                if zoom > 0.2:
                    zoom = zoom-0.2
                return HttpResponseRedirect('/segment_image/?id='+id_image+'&zoom='+str(zoom)+'&draw_segments='+str(draw_segments))
        return HttpResponseRedirect('/segment_image/?id='+id_image+'&zoom='+str(zoom)+'&draw_segments='+str(draw_segments)) 


def save_new_tags(request, image):
    #Afegim tags nous:
    post = request.POST.copy()
    tags = post.getlist('tags')
    ntag = 0
    for key in tags:
        if 'new_tag_' in key:
            tag_name = key.replace('new_tag_','')
            t = Tag(name=tag_name,image_type=image.image_type)
            t.save()
            post.getlist('tags')[ntag] = t.id
        ntag+=1
    return post
     

class EditImage(TemplateView):
    template_name='details_image.html'
    header = 'Edit Image'

    def get(self,request):
        self.request = request
        self.id_image = ''
        if 'id' in request.GET:
            self.id_image = int(request.GET['id'])
        return super(EditImage, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(EditImage, self).get_context_data(**kwargs)
        context['header'] = self.header
        if self.id_image:
            context['id_image'] = self.id_image
            image = Image.objects.get(id=self.id_image)
            context['form_image'] = ImageForm(instance=image,user=self.request.user)
        return context

    def post(self,request):
        id_image=''
        if 'id' in request.POST:
            id_image = request.POST['id']
            image = Image.objects.get(id=id_image)
            if 'btn_save_image' in request.POST:
                form_image = ImageForm(request.POST,request.FILES, instance=image) 
                if form_image.is_valid():
                    form_image.save()       
            if 'btn_return' in request.POST:
                return HttpResponseRedirect('/limages/')  
        return HttpResponseRedirect('/edit_image/?id='+id_image) 

class EditSegment(TemplateView):
    template_name='details_segment.html'
    header = 'Edit Segment'

    def get(self,request):
        self.id_segment = ''
        if 'id' in request.GET:
            self.id_segment = int(request.GET['id'])
        return super(EditSegment, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(EditSegment, self).get_context_data(**kwargs)
        context['header'] = self.header
        if self.id_segment:
            context['id_segment'] = self.id_segment
            segment = Segment.objects.get(id=self.id_segment)
            context['form_segment'] = SegmentForm(instance=segment)
        return context

    def post(self,request):
        id_segment=''
        if 'id' in request.POST:
            id_segment = request.POST['id'] 
            segment = Segment.objects.get(id=id_segment)
            if 'btn_save_segment' in request.POST:
                post = save_new_tags(request,segment.image)
                form_segment = SegmentForm(post, instance=segment) 
                if form_segment.is_valid():
                    form_segment.save()     
                else:
                    print form_segment.errors
            elif 'btn_return' in request.POST:
                return HttpResponseRedirect('/segment_image/?id='+str(segment.image_id))        
        return HttpResponseRedirect('/edit_segment/?id='+id_segment) 

class EditImageType(TemplateView):
    template_name='details_imagetype.html'
    header = 'Edit Trainning set'

    def get(self,request):
        self.request = request
        self.id_it = ''
        if 'id' in request.GET:
            self.id_it = int(request.GET['id'])
        return super(EditImageType, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(EditImageType, self).get_context_data(**kwargs)
        context['header'] = self.header
        if self.id_it:
            context['id_imagetype'] = self.id_it
            image_type = ImageType.objects.get(id=self.id_it)
            context['form_imagetype'] = ImageTypeForm(instance=image_type)#,user=self.request.user)
        return context

    def post(self,request):
        id_imagetype=''
        if 'id' in request.POST:
            id_imagetype = request.POST['id']
            image_type = ImageType.objects.get(id=id_imagetype)
            if 'btn_save_imagetype' in request.POST:
                form_imagetype = ImageTypeForm(request.POST,instance=image_type) 
                print request.POST
                if form_imagetype.is_valid():
                    form_imagetype.save()   
                else:
                    print "ERROR", str(form_imagetype.errors)
            if 'btn_return' in request.POST:
                return HttpResponseRedirect('/limages/')  
        return HttpResponseRedirect('/edit_imagetype/?id='+str(id_imagetype)) 

def get_matlab_file(request):
    if 'tags' in request.GET:
        image = ''
        identify=''
        it =''
        if 'image' in request.GET:
            image = request.GET['image']
            identify="image_"+str(image)
        if 'image_type' in request.GET:
            image_type_id = request.GET['image_type']
            it = ImageType.objects.get(id=image_type_id)
            identify="trainning_"+str(image_type_id)
        color = request.GET['image_format']
        width = request.GET['width']
        height = request.GET['height']
        ids_tags = request.GET.getlist('tags')
        tags = Tag.objects.filter(pk__in=ids_tags).order_by('name')

        temp_folder='/tmp/{0}'.format(random.randint(0,10000000))
        os.popen('mkdir {0}'.format(temp_folder))
        
        if image:
            segments = Segment.objects.filter(image=image)
        elif it:
            segments = Segment.objects.filter(image__image_type=it)
        octave=oct2py.Oct2Py()
        octave.put('labels',[t.name for t in tags])
        octave.run("addpath('/home/coneptum/segment/octave');")
        y=[]
        images=[]
        for segment in segments:
            segment_tags = []
            l=[]
            for tag in tags:
                if tag in segment.tags.all():
                    l.append(1)
                else:
                    l.append(0)
            y.append(l)
            im=PIL.Image.open(BASE_DIR+'/segment/static/'+segment.filename)
            im2=im.resize((int(width),int(height)),PIL.Image.ANTIALIAS)
            route=segment.filename.split('/')
            tmp_img='{0}/{1}'.format(temp_folder,route[len(route)-1])#.replace('jpg','png')
            if color=='gray_scale':
                im2=im2.convert('L')
            im2.save(tmp_img,'JPEG')
            if color=='edges':
                SimpleCV.Image(tmp_img).edges().save(tmp_img)
            images.append(tmp_img)
        octave.put('y',numpy.array(y))
        octave.put('images',images)
        print images
        octave.run('X=load_images(images);')
        filemat='{0}/data.mat'.format(temp_folder)
        print "filemat",filemat
        if color=='color':
            octave.run('''save {0} X y labels '''.format(filemat))
        else:
            octave.run('''save {0} X y labels'''.format(filemat))
        response = HttpResponse(open(filemat).read(), mimetype = "application/x-matlab")
        response['Content-Disposition'] = 'attachment; filename=%s' % 'data.mat'
        return response




def get_zip_file(request):
    if 'tags' in request.GET:
        image = ''
        identify=''
        it =''
        if 'image' in request.GET:
            image = request.GET['image']
            identify="image_"+str(image)
        if 'image_type' in request.GET:
            image_type_id = request.GET['image_type']
            it = ImageType.objects.get(id=image_type_id)
            identify="trainning_"+str(image_type_id)
        color = request.GET['image_format']
        print "Color",color
        width = request.GET['width']
        height = request.GET['height']
        tags = request.GET.getlist('tags')
        zip_subdir = "segments_%s" % identify
        zip_filename = "%s.zip" % zip_subdir
        s = StringIO.StringIO()
        zf = zipfile.ZipFile(s, "w")
        temp_folder='/tmp/{0}'.format(random.randint(0,10000000))
        os.popen('mkdir {0}'.format(temp_folder))
        for tag in tags:
            filenames = []
            id_tag = int(tag)
            t = Tag.objects.get(id=id_tag)
            if image:
                segments = Segment.objects.filter(tags=t,image=image)
            elif it:
                segments = Segment.objects.filter(tags=t,image__image_type=it)
            for segment in segments:
                filenames.append(BASE_DIR+'/segment/static/'+segment.filename)
            zip_path = zip_subdir+'/'+t.name
            for fpath in filenames:
                fdir, fname = os.path.split(fpath)
                zip_path2 = os.path.join(zip_path, fname)
                
                im=PIL.Image.open(fpath)
                print "w,h",width,height
                im2=im.resize((int(width),int(height)),PIL.Image.ANTIALIAS)
                if color=='gray_scale':
                    im2=im2.convert('L')
                route=fpath.split('/')
                tmp_img='{0}/{1}'.format(temp_folder,route[len(route)-1])#.replace('jpg','png')
                print "tmp_img",tmp_img
                im2.save(tmp_img,'JPEG')
                if color=='edges':
                    SimpleCV.Image(tmp_img).edges().save(tmp_img) 
                
                def_path=fpath
                
                zf.write(tmp_img, zip_path2)
        zf.close()   
        response = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return response


def post_create_user(sender, instance, created, **kwargs):
    print "Post save emited for", instance
    users = User.objects.filter(username="user_template")
    if created and len(users) > 0:
        user_template = users[0]
        print "user_template", user_template
        user = instance
        image_types = ImageType.objects.filter(user=user_template)
        print "image_types", image_types
        print 'mkdir {0}{1}'.format(BASE_DIR+'/segment/static/uploads/',str(user_template.id),str(user.id))
        os.popen('cp -a {0}{1} {0}{2}'.format(BASE_DIR+'/segment/static/uploads/',str(user_template.id),str(user.id)))
        for image_type in image_types:
            print "imagetype", image_type
            #folder_random_name = get_random_name()
            #print 'mkdir {0}{1}/{2}'.format(BASE_DIR+'/segment/static/uploads/',str(user.id),folder_random_name)
            #os.popen('mkdir {0}{1}/{2}'.format(BASE_DIR+'/segment/static/uploads/',str(user.id),folder_random_name))
            #os.popen('mkdir {0}{1}/{2}/segments'.format(BASE_DIR+'/segment/static/uploads/',str(user.id),folder_random_name))
            #os.popen('mkdir {0}{1}/{2}/segments'.format(BASE_DIR+'/segment/static/uploads/',str(user.id),folder_random_name))
            it = ImageType()
            it.name=image_type.name
            it.user = user
            it.folder = image_type.folder
            it.save()
            it.users_shared.add(user)
            tags = Tag.objects.filter(image_type=image_type)
            for tag in tags:
                t = Tag()
                t.name = tag.name
                t.image_type = it
                t.save()
            images = Image.objects.filter(image_type=image_type)
            print "images", images
            for image in images:
                i = Image()
                i.name = image.name
                i.image_type = it
                i.filename = str(image.filename).replace('/'+str(user_template.id)+'/','/'+str(user.id)+'/')
                #print 'cp "{0}{1}" "{2}{3}"'.format(BASE_DIR+'/segment/static/',str(image.filename),BASE_DIR+'/segment/static/' ,str(i.filename))
                #os.popen('cp "{0}{1}" "{2}{3}"'.format(BASE_DIR+'/segment/static/',str(image.filename),BASE_DIR+'/segment/static/' ,str(i.filename)))
                i.parent_segment = image.parent_segment
                i.save()
                segments = Segment.objects.filter(image=image)
                print "image id", image.id, "segments", len(segments), segments
                for segment in segments:
                    s = Segment()
                    s.x1 = segment.x1
                    s.y1 = segment.y1
                    s.x2 = segment.x2
                    s.y2 = segment.y2
                    s.image = i
                    s.filename = str(segment.filename).replace('/'+str(user_template.id)+'/','/'+str(user.id)+'/')
                    #print 'cp "{0}{1}" "{2}{3}"'.format(BASE_DIR+'/segment/static/',str(segment.filename),BASE_DIR+'/segment/static/',str(s.filename))
                    #os.popen('cp "{0}{1}" "{2}{3}"'.format(BASE_DIR+'/segment/static/',str(segment.filename),BASE_DIR+'/segment/static/',str(s.filename)))
                    s.save()
                    for tag in segment.tags.all():
                        tag_new = Tag.objects.filter(image_type=it,name=tag.name)
                        s.tags.add(tag_new[0])
            #Copiar carpetes amb imatges
                
        

signals.post_save.connect(post_create_user, sender=User)






