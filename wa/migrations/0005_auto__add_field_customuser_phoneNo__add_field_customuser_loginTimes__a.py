# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CustomUser.phoneNo'
        db.add_column(u'wa_customuser', 'phoneNo',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'CustomUser.loginTimes'
        db.add_column(u'wa_customuser', 'loginTimes',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'CustomUser.points'
        db.add_column(u'wa_customuser', 'points',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CustomUser.phoneNo'
        db.delete_column(u'wa_customuser', 'phoneNo')

        # Deleting field 'CustomUser.loginTimes'
        db.delete_column(u'wa_customuser', 'loginTimes')

        # Deleting field 'CustomUser.points'
        db.delete_column(u'wa_customuser', 'points')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'codename',)", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'wa.book': {
            'Meta': {'object_name': 'Book'},
            'aBookDownloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'bookName': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dBookDownloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wa.Language']"}),
            'percentageAudioInvalid': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'percentageCompleteAudio': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'percentageCompleteDigi': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'wa.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '254'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'languages_known': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'loginTimes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phoneNo': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'wa.document': {
            'Meta': {'object_name': 'Document'},
            'docfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wa.language': {
            'Meta': {'object_name': 'Language'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'langName': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'wa.paragraph': {
            'Meta': {'object_name': 'Paragraph'},
            'audioAssignedTo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'audioAssignedTo'", 'to': u"orm['wa.CustomUser']"}),
            'audioReadBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'audioReadBy'", 'to': u"orm['wa.CustomUser']"}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wa.Book']"}),
            'digiAssignedTo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'digiAssignedTo'", 'to': u"orm['wa.CustomUser']"}),
            'digiBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'digiBy'", 'to': u"orm['wa.CustomUser']"}),
            'downVotes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isChapter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isDigitizing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isRecording': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'upVotes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'validAudioVersionNumber': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'wa.userhistory': {
            'Meta': {'object_name': 'UserHistory'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'audioVersion': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loginTime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'logoutTime': ('django.db.models.fields.DateTimeField', [], {}),
            'paragraph': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wa.Paragraph']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wa.CustomUser']"}),
            'vote': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '2'})
        }
    }

    complete_apps = ['wa']