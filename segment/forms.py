# -*- coding: utf-8 -*-
from django import forms
from models import Image, Segment
from django.forms import ModelForm



class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['name', 'filename', 'image_type']

class SegmentForm(ModelForm):
    class Meta:
        model = Segment
        fields = ['x1', 'y1', 'x2','y2','image','tags']


