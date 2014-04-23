# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table(u'segment_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('image_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['segment.ImageType'])),
        ))
        db.send_create_signal(u'segment', ['Tag'])

        # Adding model 'ImageType'
        db.create_table(u'segment_imagetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['segment.Image'])),
        ))
        db.send_create_signal(u'segment', ['ImageType'])


    def backwards(self, orm):
        # Deleting model 'Tag'
        db.delete_table(u'segment_tag')

        # Deleting model 'ImageType'
        db.delete_table(u'segment_imagetype')


    models = {
        u'segment.image': {
            'Meta': {'object_name': 'Image'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'segment.imagetype': {
            'Meta': {'object_name': 'ImageType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['segment.Image']"}),
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