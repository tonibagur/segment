# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'segment_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75, db_index=True)),
            ('joined', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'segment', ['User'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'segment_user')


    models = {
        u'segment.image': {
            'Meta': {'object_name': 'Image'},
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['segment.ImageType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent_segment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'parent_segment'", 'null': 'True', 'to': u"orm['segment.Segment']"})
        },
        u'segment.imagetype': {
            'Meta': {'object_name': 'ImageType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'segment.segment': {
            'Meta': {'object_name': 'Segment'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['segment.Image']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['segment.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'x1': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'x2': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'y1': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'y2': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'segment.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['segment.ImageType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'segment.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['segment']