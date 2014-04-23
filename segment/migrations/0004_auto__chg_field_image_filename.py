# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Image.filename'
        db.alter_column(u'segment_image', 'filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100))

    def backwards(self, orm):

        # Changing field 'Image.filename'
        db.alter_column(u'segment_image', 'filename', self.gf('django.db.models.fields.CharField')(max_length=50))

    models = {
        u'segment.image': {
            'Meta': {'object_name': 'Image'},
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['segment.ImageType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'segment.imagetype': {
            'Meta': {'object_name': 'ImageType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'segment.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['segment.ImageType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['segment']