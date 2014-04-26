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



def log(s):
    print s

def home(request):
    p = "/limages/"
    return HttpResponseRedirect(p)


class LImages(ListView):
    model = Image #implies -> queryset = models.Car.objects.all()
    template_name = 'limages.html' #optional (this is the default name)
    context_object_name = "images" #default is object_list
    paginate_by = 50 #and that's it !!
    base_url= '/limages/'
    view_name = 'LImages'
    header = 'Images list'

    def get(self,request):
        self.id_image = ''
        self.image_type_sel = 1 #Default
        if 'image_type' in request.GET:
            self.image_type_sel = int(request.GET['image_type'])
        self.queryset = Image.objects.filter(image_type_id=self.image_type_sel)
        return super(LImages, self).get(request)
 
    def get_context_data(self, **kwargs):
        context = super(LImages, self).get_context_data(**kwargs)
        context['header'] = self.header
        context['form_image'] = ImageForm()
        context['image_types'] = ImageType.objects.all()
        context['image_type_sel'] = self.image_type_sel
        return context

    def post(self,request):
        image_type = ''
        if 'image_type_sel' in request.POST:
            image_type = request.POST['image_type_sel']
        if 'btn_create_image' in request.POST:
            form_image = ImageForm(request.POST,request.FILES) 
            if form_image.is_valid():
                form_image.save()
        if 'btn_remove_image' in request.POST:
            id_image = request.POST['selected_row']
            image = Image.objects.get(id = id_image)
            if image:
                filepath = BASE_DIR+'/segment/static/'+str(image.filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                image.delete()
        return HttpResponseRedirect('/limages/?image_type='+str(image_type)) 


class SegmentImage(TemplateView):
    template_name='segment_image.html'
    header = 'Segment Image'

    def get(self,request):
        self.id_image = ''
        self.zoom = 1
        self.draw_segments = False
        if 'id' in request.GET:
            self.id_image = int(request.GET['id'])
            if 'zoom' in request.GET:
                self.zoom = request.GET['zoom'] or 1
            if 'draw_segments' in request.GET and request.GET['draw_segments'] == 'True':
                self.draw_segments=True
        return super(SegmentImage, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(SegmentImage, self).get_context_data(**kwargs)
        context['header'] = self.header
        if self.id_image:
            context['id_image'] = self.id_image
            image = Image.objects.get(id=self.id_image)
            context['form'] = ImageForm(instance=image)
            new_segment = Segment(image=image)
            context['form_segment'] = SegmentForm(instance=new_segment)
            context['segments'] = Segment.objects.filter(image_id=self.id_image)
            context['form_generate_image'] = GenerateImagesForm()
            context['zoom'] = self.zoom
            context['draw_segments'] = self.draw_segments
        return context

    def post(self,request):
        id_image=zoom=''
        if 'image' in request.POST:
            id_image = request.POST['image']
            path_segments = BASE_DIR+'/segment/static/uploads/segments/'
            draw_segments='false'
            if 'zoom' in request.POST:
                zoom = float(request.POST['zoom'])
            if 'draw_segments' in request.POST:
                draw_segments = request.POST['draw_segments']
            if 'btn_create_segment' in request.POST:
                form_segment = SegmentForm(request.POST) 
                if form_segment.is_valid():
                    try:   
                        #TODO primer crear imatge i dsp guardar segment, no a l'inreves
                        segment = form_segment.save()   #commit=False  
                        filename = 'segment_'+str(id_image)+"_"+str(segment.id)+'.jpg'
                        segment.filename = 'uploads/segments/'+filename
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
                        image.name = segment.filename.split('/')[2].split('.jpg')[0]
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
    header = 'Image details'

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
    header = 'Details Segment'

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






