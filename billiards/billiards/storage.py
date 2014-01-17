# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年01月4日

@author: baron
'''

from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousOperation
from billiards import settings
from billiards.settings import BCS_BUCKET
from billiards.support import pybcs
import unicodedata
import os

# set bucket
AK = BCS_BUCKET['AK']
SK = BCS_BUCKET['SK']
BUCKET_NAME = BCS_BUCKET['BUCKET_NAME']
BCS_SITE = BCS_BUCKET['BCS_SITE']

class BcsStorage(FileSystemStorage):
    """
    这是一个支持bcs和本地django的FileStorage基类
    修改存储文件的路径和基本url
    """
    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        super(BcsStorage, self).__init__(location, base_url)

    @property
    def maxsize(self):
        return 10*1024*1024

    @property
    def filetypes(self):
        return []
    
    def get_available_name(self, name):
        return name.encode('utf8')
    
    def get_valid_name(self, name):
        try:
            name = unicodedata.normalize('NFKD', name).encode('utf8')
        except Exception:
            name = "%s.jpg"%type(name)
        #end
        return super(BcsStorage, self).get_valid_name(name)
    
    def connect_bucket(self):
        """
        Connect to the bcs bucket.
        """
        try:
            bcs = pybcs.BCS(BCS_SITE, AK, SK, pybcs.HttplibHTTPC)
            bkt = bcs.bucket(BUCKET_NAME)
            bkt.get_acl()['body']
            return bkt
        except Exception as e:
            print (e)
            raise
        
    def get_object(self, bkt, file_path):
        """
        Get or create an object from or on the bucket.
        """
        path = file_path
        
        if path[0] != '/':
            path = '/' + path
        return bkt.object(path)

    def _save(self, name, content):
        """
        Save file on the bcs bucket.
        """
        hz = name.split(".")[-1]
        # judge type
        if self.filetypes!='*':
            if hz.lower() not in self.filetypes:
                raise SuspiciousOperation(u"不支持的文件类型,支持%s"%self.filetypes)
        
        rename = self.makename(name)
        # judge size
        if content.size > self.maxsize:
            raise SuspiciousOperation(u"文件大小超过限制")

        bkt = self.connect_bucket()
        obj = bkt.object(rename)

        if hasattr(content, '_get_file'):  # admin entry
            obj.put(content._get_file().read())
        else:   # view entry（ContentFile）
            obj.put(content.read())
        
        return rename

# Rename the file name to a unique string + file name
    def makename(self, name):
        basename = os.path.basename(name)
        path = os.path.dirname(name)
        
        try:
            fname, hk = basename.split('.')
        except:
            fname, hk = basename, ''
        
        random_string = ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(16)))
        
        if hk:
            rename = "%s_%s.%s" % (random_string, fname, hk)
        else:
            rename = "%s_%s" % (random_string, fname)
        rename = os.path.join(path, rename)
        return rename

    def delete(self,name):
        """
        Delete a file from bcs.
        """
        bkt = self.connect_bucket()
        obj = bkt.object(name)
        
        try:
            obj.delete()
        except Exception:
            pass
        
    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return self.base_url+name
        
class ImageStorage(BcsStorage):
    """
    Implementation of a Storage for ImageField.
    """
    @property
    def maxsize(self):
        return 10*1024*1024 # max size 10M

    @property
    def filetypes(self):
        return ['jpg','jpeg','png','gif']

class FileStorage(BcsStorage):
    @property
    def maxsize(self):
        return 10*1024*1024 # max size 10M

    @property
    def filetypes(self):
        return "*"
