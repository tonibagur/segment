# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Segment'
        db.create_table(u'segment_segment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('x1', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('y1', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('x2', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('y2', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['segment.Image'])),
        ))
        db.send_create_signal(u'segment', ['Segment'])

        # Adding M2M table for field tags on 'Segment'
        m2m_table_name = db.shorten_name(u'segment_segment_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('segment', models.ForeignKey(orm[u'segment.segment'], null=False)),
            ('tag', models.ForeignKey(orm[u'segment.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['segment_id', 'tag_id'])


    def backwards(self, orm):
        # Deleting model 'Segment'
        db.delete_table(u'segment_segment')

        # Removing M2M table for field tags on 'Segment'
        db.delete_table(db.shorten_name(u'segment_segment_tags'))


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
        u'segment.segment': {
            'Meta': {'object_name': 'Segment'},
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
        }
    }

    complete_apps = ['segment']