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
from segment.forms import ImageForm,SegmentForm,GenerateImagesForm
from settings import BASE_DIR
import os
import PIL
import traceback
from django.contrib.auth.decorators import login_required
from collections import OrderedDict
import random
import string
import zipfile
import StringIO




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
        self.image_types = ImageType.objects.filter(user_id=request.user.id).order_by('name')
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
                group = {'image_type':type,'rows':[]}
            group['rows'].append(image)
        images_in_type.append(group)
        self.queryset = images_in_type
        return super(LImages, self).get(request)
 
    def get_context_data(self, **kwargs):
        context = super(LImages, self).get_context_data(**kwargs)
        context['header'] = self.header
        context['form_image'] = ImageForm()
        context['image_types'] = self.image_types
        context['download_tags'] = Tag.objects.all().order_by('name')
        return context

    def post(self,request):
        if 'btn_create_image' in request.POST:
            form_image = ImageForm(request.POST,request.FILES) 
            if form_image.is_valid():
                form_image.save()
        if 'btn_remove_image' in request.POST:
            id_image = request.POST['selected_row']
            self.delete_image(id_image)
        if 'btn_create_image_type' in request.POST:
            new_image_type = request.POST['name_image_type']
            folder_random_name = self.get_random_name()
            it = ImageType()
            it.name = new_image_type
            it.user = request.user
            it.folder = folder_random_name
            it.save()
        if 'btn_delete_image_type' in request.POST:
            image_type = request.POST['image_type']
            it = ImageType.objects.get(id=image_type)
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
        return HttpResponseRedirect('/limages/') 

    def delete_image(self, id_image):
        image = Image.objects.get(id = id_image)
        if image:
            filepath = BASE_DIR+'/segment/static/'+str(image.filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
            image.delete()

    def get_random_name(self):
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
            context['form'] = ImageForm(instance=image)
            new_segment = Segment(image=image)
            context['form_segment'] = SegmentForm(instance=new_segment)
            segments = Segment.objects.filter(image_id=self.id_image)
            context['segments'] = segments
            context['form_generate_image'] = GenerateImagesForm()
            context['zoom'] = self.zoom
            context['draw_segments'] = self.draw_segments
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
                form_generate_images = GenerateImagesForm(request.POST)
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


class EditImage(TemplateView):
    template_name='details_image.html'
    header = 'Edit Image'

    def get(self,request):
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
            context['form_image'] = ImageForm(instance=image)
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
                form_segment = SegmentForm(request.POST, instance=segment) 
                if form_segment.is_valid():
                    form_segment.save()     
                else:
                    print form_segment.errors
            elif 'btn_return' in request.POST:
                return HttpResponseRedirect('/segment_image/?id='+str(segment.image_id))        
        return HttpResponseRedirect('/edit_segment/?id='+id_segment) 


def get_matlab_file(request):
    if 'image' in request.GET:
        id_image = request.GET['id_image']
        color = request.GET['image_format']
        #TODO TBC
        '''temp_path = settings.STATIC_ROOT + filename
        wb = Workbook(StringIO.StringIO())
        ws = wb.create_sheet()
        for row in rows:
            new_row=[]
            for col in row:
                    new_row.append(col)
            ws.append(new_row)
        wb.save(temp_path)
        s=StringIO.StringIO()
        s.write(open(temp_path).read())
        s.seek(0)
        response = HttpResponse(s,content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s"' %(filename,)
        os.remove(temp_path)
        return response'''
    return HttpResponseRedirect('/')




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
        tags = request.GET.getlist('tags')
        zip_subdir = "segments_%s" % identify
        zip_filename = "%s.zip" % zip_subdir
        s = StringIO.StringIO()
        zf = zipfile.ZipFile(s, "w")
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
                zf.write(fpath, zip_path2)
        zf.close()   
        response = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return response







