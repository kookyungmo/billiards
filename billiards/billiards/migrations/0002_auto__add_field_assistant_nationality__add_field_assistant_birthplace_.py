# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Assistant.nationality'
        db.add_column('assistant', 'nationality',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16),
                      keep_default=False)

        # Adding field 'Assistant.birthplace'
        db.add_column('assistant', 'birthplace',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=24),
                      keep_default=False)

        # Adding field 'Assistant.constellation'
        db.add_column('assistant', 'constellation',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=8),
                      keep_default=False)

        # Adding field 'Assistant.measurements'
        db.add_column('assistant', 'measurements',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=24),
                      keep_default=False)

        # Adding field 'Assistant.experience'
        db.add_column('assistant', 'experience',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Assistant.favoriteplayers'
        db.add_column('assistant', 'favoriteplayers',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64),
                      keep_default=False)

        # Adding field 'Assistant.selfintroduce'
        db.add_column('assistant', 'selfintroduce',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1024),
                      keep_default=False)

        # Adding field 'Assistant.bestperformance'
        db.add_column('assistant', 'bestperformance',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Assistant.nationality'
        db.delete_column('assistant', 'nationality')

        # Deleting field 'Assistant.birthplace'
        db.delete_column('assistant', 'birthplace')

        # Deleting field 'Assistant.constellation'
        db.delete_column('assistant', 'constellation')

        # Deleting field 'Assistant.measurements'
        db.delete_column('assistant', 'measurements')

        # Deleting field 'Assistant.experience'
        db.delete_column('assistant', 'experience')

        # Deleting field 'Assistant.favoriteplayers'
        db.delete_column('assistant', 'favoriteplayers')

        # Deleting field 'Assistant.selfintroduce'
        db.delete_column('assistant', 'selfintroduce')

        # Deleting field 'Assistant.bestperformance'
        db.delete_column('assistant', 'bestperformance')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'access_token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'null': 'True'}),
            'avatar': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True'}),
            'cellphone': ('django.db.models.fields.CharField', [], {'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'expire_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '1', 'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'null': 'True'}),
            'site_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'null': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'billiards.assistant': {
            'Meta': {'object_name': 'Assistant', 'db_table': "'assistant'"},
            'bestperformance': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'birthday': ('django.db.models.fields.DateField', [], {}),
            'birthplace': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'constellation': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'dress': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'drinks': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'experience': ('django.db.models.fields.IntegerField', [], {}),
            'favoriteplayers': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'figure': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'food': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'gender': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'haircolor': ('billiards.models.ChoiceTypeField', [], {'max_length': '16'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'language': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            'measurements': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'nationality': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'pubichair': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'scent': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'selfintroduce': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'state': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        u'billiards.assistantappointment': {
            'Meta': {'object_name': 'AssistantAppointment', 'db_table': "'assistant_appoinment'"},
            'assitant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Assistant']"}),
            'createdDate': ('django.db.models.fields.DateTimeField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'endtime': ('django.db.models.fields.DateTimeField', [], {}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Goods']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poolroom': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'state': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Transaction']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'billiards.assistantimage': {
            'Meta': {'object_name': 'AssistantImage', 'db_table': "'assistant_images'"},
            'assistant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Assistant']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagepath': ('django.db.models.fields.files.ImageField', [], {'max_length': '250'}),
            'iscover': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'billiards.assistantoffer': {
            'Meta': {'object_name': 'AssistantOffer', 'db_table': "'assistant_offer'"},
            'assistant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Assistant']"}),
            'day': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            'endtime': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poolroom': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'starttime': ('django.db.models.fields.TimeField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'billiards.challenge': {
            'Meta': {'object_name': 'Challenge', 'db_table': "'challenge'"},
            'expiretime': ('django.db.models.fields.DateTimeField', [], {}),
            'geolocation': ('geosimple.fields.GeohashField', [], {'db_index': 'True', 'max_length': '12', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['billiards.Group']", 'db_column': "'group'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'issuer_contact': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'issuer_nickname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '7'}),
            'lat_baidu': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '7'}),
            'level': ('billiards.models.ChoiceTypeField', [], {'max_length': '12'}),
            'lng': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '7'}),
            'lng_baidu': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '7'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'participant_count': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'poolroom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Poolroom']", 'db_column': "'poolroom'"}),
            'rule': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'source': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('billiards.models.ChoiceTypeField', [], {'default': "'waiting'", 'max_length': '7'}),
            'tabletype': ('billiards.models.ChoiceTypeField', [], {'max_length': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        u'billiards.challengeapply': {
            'Meta': {'unique_together': "(('challenge', 'user'),)", 'object_name': 'ChallengeApply', 'db_table': "'challenge_apply'"},
            'applytime': ('django.db.models.fields.DateTimeField', [], {}),
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Challenge']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('billiards.models.ChoiceTypeField', [], {'default': "'submitted'", 'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'billiards.coupon': {
            'Meta': {'object_name': 'Coupon', 'db_table': "'coupon'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'discount': ('django.db.models.fields.IntegerField', [], {'max_length': '3'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poolroom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Poolroom']"}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'status': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'billiards.event': {
            'Meta': {'object_name': 'Event', 'db_table': "'event'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'enddate': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'pagename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'picAD': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'titleabbrev': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'billiards.eventcode': {
            'Meta': {'object_name': 'EventCode', 'db_table': "'eventcode'"},
            'chargecode': ('django.db.models.fields.CharField', [], {'default': "'QP0UTOE'", 'max_length': '10'}),
            'createdtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 12, 0, 0)'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poolroom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Poolroom']"}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'usedtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'userid': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'billiards.goods': {
            'Meta': {'object_name': 'Goods', 'db_table': "'goods'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'price': ('billiards.models.CurrencyField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'sku': ('django.db.models.fields.CharField', [], {'default': "'BCOJO58V1W4QDPCYZWX8GVGZNJC8RTLL'", 'max_length': '32'}),
            'state': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'type': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'})
        },
        u'billiards.group': {
            'Meta': {'object_name': 'Group', 'db_table': "'fans_group'"},
            'cardimg': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'billiards.match': {
            'Meta': {'object_name': 'Match', 'db_table': "'match'"},
            'bonus': ('django.db.models.fields.FloatField', [], {}),
            'bonusdetail': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'enrollfee': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'enrollfocal': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'flags': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organizer': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['billiards.Group']", 'db_column': "'organizer'"}),
            'otherprize': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'poolroom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Poolroom']"}),
            'rechargeablecard': ('django.db.models.fields.FloatField', [], {}),
            'rule': ('django.db.models.fields.TextField', [], {}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('billiards.models.ChoiceTypeField', [], {'default': "'approved'", 'max_length': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'})
        },
        u'billiards.matchenroll': {
            'Meta': {'object_name': 'MatchEnroll', 'db_table': "'match_enroll'"},
            'enrolltime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Match']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'billiards.membership': {
            'Meta': {'object_name': 'Membership', 'db_table': "'membership'"},
            'cellphone': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'gender': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'joindate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 12, 0, 0)'}),
            'memberid': ('django.db.models.fields.CharField', [], {'default': "'31476480290'", 'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'targetid': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['billiards.Group']", 'db_column': "'target_group'"}),
            'userid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'wechatid': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'billiards.payaccount': {
            'Meta': {'object_name': 'PayAccount', 'db_table': "'payaccount'"},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'pid': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'type': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'})
        },
        u'billiards.poolroom': {
            'Meta': {'object_name': 'Poolroom', 'db_table': "'poolroom'"},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'businesshours': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'city': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'exist': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'flags': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '7'}),
            'lat_baidu': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '7'}),
            'lng': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '7'}),
            'lng_baidu': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '7'}),
            'location': ('geosimple.fields.GeohashField', [], {'max_length': '12', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'max_length': '2', 'null': 'True'}),
            'review': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        u'billiards.poolroomequipment': {
            'Meta': {'object_name': 'PoolroomEquipment', 'db_table': "'poolroomequipment'"},
            'cue': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poolroom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Poolroom']"}),
            'price': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True'}),
            'producer': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True'}),
            'tabletype': ('billiards.models.ChoiceTypeField', [], {'max_length': '10'})
        },
        u'billiards.poolroomimage': {
            'Meta': {'object_name': 'PoolroomImage', 'db_table': "'poolroom_images'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagepath': ('django.db.models.fields.files.ImageField', [], {'max_length': '250'}),
            'iscover': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'poolroom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Poolroom']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'billiards.poolroomuser': {
            'Meta': {'object_name': 'PoolroomUser', 'db_table': "'poolroom_user'"},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['billiards.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poolroom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Poolroom']"}),
            'type': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'billiards.poolroomuserapply': {
            'Meta': {'object_name': 'PoolroomUserApply', 'db_table': "'poolroom_user_application'"},
            'applytime': ('django.db.models.fields.DateTimeField', [], {}),
            'cellphone': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'justification': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'poolroom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Poolroom']"}),
            'poolroomname_userinput': ('django.db.models.fields.CharField', [], {'default': 'True', 'max_length': '50', 'null': 'True'}),
            'realname': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status': ('billiards.models.ChoiceTypeField', [], {'default': "'submitted'", 'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'billiards.transaction': {
            'Meta': {'object_name': 'Transaction', 'db_table': "'transaction'"},
            'buyeid': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'buyerEmail': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'closedDate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'createdDate': ('django.db.models.fields.DateTimeField', [], {}),
            'fee': ('billiards.models.CurrencyField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'goods': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.Goods']", 'db_column': "'goods'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notifyid': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'paidDate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'payaccount': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billiards.PayAccount']", 'db_column': "'payaccount'"}),
            'paytradeNum': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'state': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'tradeStatus': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'tradenum': ('django.db.models.fields.CharField', [], {'default': "'OH60PI9OV7DGM5LU1VUYWZSY2UHIH4JKP34W41M2L9OB5BHQXWQYAG92CR93WJ88'", 'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'db_column': "'uid'"})
        },
        u'billiards.wechatactivity': {
            'Meta': {'object_name': 'WechatActivity', 'db_table': "'wechat_activity'"},
            'eventtype': ('billiards.models.ChoiceTypeField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'receivedtime': ('django.db.models.fields.DateTimeField', [], {}),
            'reply': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'target': ('billiards.models.IntegerChoiceTypeField', [], {'default': '1'}),
            'userid': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'billiards.wechatcredential': {
            'Meta': {'object_name': 'WechatCredential', 'db_table': "'wechat_credential'"},
            'appid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['billiards']