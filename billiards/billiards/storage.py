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
        
#         name = self.makename(name)
        # judge size
        if content.size > self.maxsize:
            raise SuspiciousOperation(u"文件大小超过限制")

        bkt = self.connect_bucket()
        obj = bkt.object(name)

        if hasattr(content, '_get_file'):  # admin entry
            obj.put(content._get_file().read())
        else:   # view entry（ContentFile）
            obj.put(content.read())
        
        return name


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
