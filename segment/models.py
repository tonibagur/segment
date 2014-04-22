# -*- coding: utf-8 -*-
from django.db import models
import settings
import base64
import sys
import random
reload(sys)
sys.setdefaultencoding("utf-8")


class Image(models.Model):
    name = models.CharField(max_length=50)
    filename = models.CharField(max_length=50)

