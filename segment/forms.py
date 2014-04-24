# -*- coding: utf-8 -*-
from django import forms
from models import Image, Segment,Tag,ImageType
from django.forms import ModelForm



class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['name', 'filename', 'image_type']

class SegmentForm(ModelForm):
    class Meta:
        model = Segment
        fields = ['x1', 'y1', 'x2','y2','image','tags','filename']

    def __init__(self, *args, **kwargs):
       super(SegmentForm, self).__init__(*args, **kwargs)
       #Filtrem tags del segment segons el tipo de imatge al que pertanyen
       if 'instance' in kwargs and kwargs['instance'].image.image_type.id:
           image_type_filter = kwargs['instance'].image.image_type.id
           self.fields['tags'].queryset = Tag.objects.filter(image_type=image_type_filter)

class GenerateImageForm(forms.Form):
    image_type = forms.ModelChoiceField(queryset=ImageType.objects.all())
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all())





