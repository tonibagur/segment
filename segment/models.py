# -*- coding: utf-8 -*-
from django.db import models
import settings
import base64
import sys
import random
reload(sys)
sys.setdefaultencoding("utf-8")
from settings import BASE_DIR


class ImageType(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Image(models.Model):
    name = models.CharField(max_length=50)
    filename = models.ImageField(upload_to='uploads/')
    image_type = models.ForeignKey(ImageType) 
    parent_image = models.ForeignKey('self', null=True)   

    def __unicode__(self):
        return self.name

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
    image = models.ForeignKey(Image)                                                                                                                                                             
    tags = models.ManyToManyField(Tag,blank=True)
    filename = models.CharField(max_length=200,blank=True)
    

    

