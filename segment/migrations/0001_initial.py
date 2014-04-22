# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Image'
        db.create_table(u'segment_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'segment', ['Image'])


    def backwards(self, orm):
        # Deleting model 'Image'
        db.delete_table(u'segment_image')


    models = {
        u'segment.image': {
            'Meta': {'object_name': 'Image'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['segment']