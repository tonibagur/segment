# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Image.image_type'
        db.add_column(u'segment_image', 'image_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['segment.ImageType']),
                      keep_default=False)

        # Deleting field 'ImageType.image'
        db.delete_column(u'segment_imagetype', 'image_id')


    def backwards(self, orm):
        # Deleting field 'Image.image_type'
        db.delete_column(u'segment_image', 'image_type_id')

        # Adding field 'ImageType.image'
        db.add_column(u'segment_imagetype', 'image',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['segment.Image']),
                      keep_default=False)


    models = {
        u'segment.image': {
            'Meta': {'object_name': 'Image'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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