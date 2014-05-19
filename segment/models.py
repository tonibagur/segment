# -*- coding: utf-8 -*-
from django.db import models
import settings
import base64
import sys
import random
reload(sys)
sys.setdefaultencoding("utf-8")
from settings import BASE_DIR
from django.contrib.auth.models import User



class ImageType(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User)
    users_shared = models.ManyToManyField(User,related_name='users_shared', blank=True, null=True)
    folder = models.CharField(max_length=50,blank=True)

    def __unicode__(self):
        return self.name

    def get_count_images(self):
        return len(Image.objects.filter(image_type=self)) 

    def get_tags(self):
        return Tag.objects.filter(image_type=self)


class Tag(models.Model):
    name = models.CharField(max_length=50)
    image_type = models.ForeignKey(ImageType)

    def __unicode__(self):
        return self.name

class Segment(models.Model):
    x1 = models.FloatField(default=0)
    y1 = models.FloatField(default=0)
    x2 = models.FloatField(default=0)
    y2 = models.FloatField(default=0)   
    image = models.ForeignKey('Image')                                                                                                                                                             
    tags = models.ManyToManyField(Tag,blank=True)
    filename = models.CharField(max_length=200,blank=True)

def upload_to(instance, filename):
    return 'uploads/%s/%s/%s' % (instance.image_type.user.id,instance.image_type.folder, filename)

class Image(models.Model):
    name = models.CharField(max_length=50)
    filename = models.ImageField(upload_to=upload_to)
    image_type = models.ForeignKey(ImageType) 
    parent_segment = models.ForeignKey('Segment', related_name='parent_segment', blank=True, null=True)    

    def __unicode__(self):
        return self.name

    def get_count_segments(self):
        return len(Segment.objects.filter(image=self)) 






    

    

