# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from models import Image, ImageType
from segment.forms import ImageForm,SegmentForm



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

 
    def get_context_data(self, **kwargs):
        context = super(LImages, self).get_context_data(**kwargs)
        context['header'] = self.header
        context['form_image'] = ImageForm()
        return context

    def post(self,request):
        if 'btn_create_image' in request.POST:
            print "request.FILES", request.FILES
            form_image = ImageForm(request.POST,request.FILES) 
            if form_image.is_valid():
                form_image.save()
        if 'btn_remove_image' in request.POST:
            id_image = request.POST['selected_row']
            image = Image.objects.get(id = id_image)
            if image:
                image.delete()
        return HttpResponseRedirect('/limages/') 


class SegmentImage(TemplateView):
    template_name='segment_image.html'
    header = 'Segment Image'


    def get(self,request):
        self.id_image = ''
        if 'id' in request.GET:
            self.id_image = int(request.GET['id'])
        return super(SegmentImage, self).get(request)


    def get_context_data(self, **kwargs):
        context = super(SegmentImage, self).get_context_data(**kwargs)
        context['header'] = self.header
        if self.id_image:
            context['id_image'] = self.id_image
            image = Image.objects.get(id=self.id_image)
            context['form'] = ImageForm(instance=image)
            context['form_segment'] = SegmentForm()
            print context['form']
        return context

    def post(self,request):
        id_image=''
        if 'image' in request.POST:
            id_image = request.POST['image']
        if 'btn_create_segment' in request.POST:
            form_segment = SegmentForm(request.POST) 
            if form_segment.is_valid():
                form_segment.save()
            
        return HttpResponseRedirect('/segment_image/?id='+id_image) 






