# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from models import Image



def log(s):
    print s

def home(request):
    p = "/limages/"
    return HttpResponseRedirect(p)


class LImages(ListView):
    model = Image #implies -> queryset = models.Car.objects.all()
    template_name = 'limages.html' #optional (this is the default name)
    context_object_name = "image" #default is object_list
    paginate_by = 50 #and that's it !!
    base_url= '/limages/'
    view_name = 'LImages'
    header = 'Llista imatges'

 
    def get_context_data(self, **kwargs):
        context = super(LImages, self).get_context_data(**kwargs)
        context['header'] = self.header
        return context
