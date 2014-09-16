# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2014年9月16日

@author: kane
'''
from django.test.testcases import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

class UserTest(TestCase):
    fixtures = ['group.json']
    
    def setUp(self):
        self.client = Client()
        
    def testMembershipApply(self):
        response = self.client.get(reverse('membership_apply', args=('abcd', 2)))
        self.assertEqual(response.status_code, 200)
