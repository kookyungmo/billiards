# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年6月14日

@author: kane
'''
class BilliardsRouter(object):
    """A router to control all database operations on models in
    the billiards application"""

    def db_for_read(self, model, **hints):
        "Point all operations on transaction models to 'billiards_transaction'"
        if model._meta.app_label == 'transaction':
            return 'billiards_transaction'
        return 'default'

    def db_for_write(self, model, **hints):
        "Point all operations on transaction models to 'billiards_transaction'"
        if model._meta.app_label == 'transaction':
            return 'billiards_transaction'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, db, model):
        return False