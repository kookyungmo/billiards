# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''
from billiards.models import Poolroom, Match, PoolroomEquipment, User,\
    MatchEnroll, Challenge, ChallengeApply, PoolroomUser,\
    PoolroomUserApply, PoolroomImage, Group, Coupon, WechatActivity
from django.contrib import admin
from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from bitfield.admin import BitFieldListFilter
from billiards.location_convertor import gcj2bd
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext_lazy as _

class ModelWithFlagsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }

class MatchAdmin(ModelWithFlagsAdmin):
    list_filter = (
            ('flags', BitFieldListFilter),
            )

class PoolroomAdmin(ModelWithFlagsAdmin):
    list_filter = (
            ('flags', BitFieldListFilter),
            )
    def save_model(self, request, obj, form, change):
        # custom stuff here
        if (obj.lat_baidu == 0 or obj.lng_baidu == 0) and (obj.lat != 0 and obj.lng != 0):
            baiduLoc = gcj2bd(float(obj.lat), float(obj.lng))
            obj.lat_baidu = baiduLoc[0]
            obj.lng_baidu = baiduLoc[1]
        obj.save()
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields =('avatar','id','username','password','first_name','last_name',
                 'site_name','nickname','gender','email','last_login',
                 'date_joined','is_active','is_staff','is_superuser','user_permissions',
                 'groups', 'access_token', 'expire_time', 'refresh_token', 'cellphone')

class CustomUserAdmin(UserAdmin):
    fieldsets = (
            (None, {'fields': ('username', 'password')}),
            (_('Personal info'), {'fields': ('first_name', 'last_name', 'email','cellphone')}),
            (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                           'groups', 'user_permissions')}),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
            (_('Social Site info'), {'fields': ('nickname', 'site_name', 'gender', 'avatar',
                                                'access_token', 'expire_time', 
                                                'refresh_token')}),
        )
    form = CustomUserChangeForm
    list_display = UserAdmin.list_display + ('nickname', 'site_name', 'gender', 'cellphone')
    search_fields = UserAdmin.search_fields + ('nickname', )

class ChallengeAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj is None: # add a object
            return self.readonly_fields + ('status',)
        return self.readonly_fields
    
class ChallengeApplyAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'status', 'applytime', 'verbose_username')
    def get_readonly_fields(self, request, obj=None):
        if obj is not None: # modify a object
            return self.readonly_fields + ('challenge', 'verbose_username', 'user', 'applytime',)
        return self.readonly_fields
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
class PoolroomUserAdmin(admin.ModelAdmin):
    list_display = ('poolroom', 'group', 'verbose_user', 'type')
    
class PoolroomImageAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj is not None: # modify a object
            return self.readonly_fields + ('imagetag',)
        return self.readonly_fields
          
class WechatActivityAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('userid', 'eventtype', 'message', 'receivedtime', 'reply')
    
admin.site.register(Poolroom, PoolroomAdmin)
admin.site.register(PoolroomEquipment)
admin.site.register(Match, MatchAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(MatchEnroll)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(ChallengeApply, ChallengeApplyAdmin)
admin.site.register(PoolroomImage, PoolroomImageAdmin)
admin.site.register(PoolroomUser, PoolroomUserAdmin)
admin.site.register(PoolroomUserApply)
admin.site.register(Group)
admin.site.register(Coupon)
admin.site.register(WechatActivity, WechatActivityAdmin)