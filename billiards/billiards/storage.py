# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年01月4日

@author: baron
'''

import base64
import hashlib
import os
import unicodedata

from django.core.exceptions import SuspiciousOperation
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from baidubce.auth.bce_credentials import BceCredentials
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.services.bos.bos_client import BosClient
from billiards import settings
from billiards.settings import BCS_BUCKET
from billiards.support import pybcs


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
    def __init__(self, location=settings.MEDIA_URL, base_url=settings.MEDIA_URL):
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

        self.saveToBucket(rename, content)
        return rename
    
    def saveToBucket(self, name, content):
        bkt = self.connect_bucket()
        obj = bkt.object(name)
        
        if hasattr(content, '_get_file'):  # admin entry
            obj.put(content._get_file().read())
        elif isinstance(content, (ContentFile)) :   # view entry（ContentFile）
            obj.put(content.read())
        else:
            obj.put(content)
            
        return obj

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
        
        
class BOSStorage(BcsStorage):
    bucket_name = BCS_BUCKET['BUCKET_NAME']
    """
    这是一个支持BOS和本地django的FileStorage基类
    修改存储文件的路径和基本url
    """
    def __init__(self, location=settings.MEDIA_URL, base_url=settings.MEDIA_URL):
        super(BOSStorage, self).__init__(location, base_url)
        config = BceClientConfiguration(credentials=BceCredentials(BCS_BUCKET['AK'], BCS_BUCKET['SK']), endpoint=BCS_BUCKET['END_POINT'])
        self.bos_client = BosClient(config)
        # check if bucket exists
        if not self.bos_client.does_bucket_exist(self.bucket_name):
            self.bos_client.create_bucket(self.bucket_name)
            
    def saveToBucket(self, name, content):
        data = None
        if hasattr(content, '_get_file'):  # admin entry
            data = content._get_file().read()
        elif isinstance(content, (ContentFile)) :   # view entry（ContentFile）
            data = content.read()
        else:
            data = content
        md5 = hashlib.md5()
        md5.update(data)
        md5value = base64.standard_b64encode(md5.digest())
        self.bos_client.put_object(self.bucket_name, name, data, len(data), md5value)
        
    def delete(self,name):
        """
        Delete a file from bos.
        """
        self.bos_client.delete_object(self.bucket_name, name)
                
class ImageStorage(BOSStorage):
    """
    Implementation of a Storage for ImageField.
    """
    @property
    def maxsize(self):
        return 10*1024*1024 # max size 10M

    @property
    def filetypes(self):
        return ['jpg','jpeg','png','gif']

class FileStorage(BOSStorage):
    @property
    def maxsize(self):
        return 10*1024*1024 # max size 10M

    @property
    def filetypes(self):
        return "*"
