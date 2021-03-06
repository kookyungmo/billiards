# -*- coding: utf-8 -*-
# encoding: utf-8
'''
Created on 2013年10月21日

@author: kane
'''
from billiards.models import Poolroom, Match, PoolroomEquipment, User,\
    MatchEnroll, Challenge, ChallengeApply, PoolroomUser,\
    PoolroomUserApply, PoolroomImage, Group, Coupon, WechatActivity, Event,\
    Membership, Goods, Assistant, AssistantOffer, AssistantAppointment,\
    AssistantImage, AssistantUser
from django.contrib import admin
from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from bitfield.admin import BitFieldListFilter
from billiards.location_convertor import gcj2bd
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.filters import SimpleListFilter
import datetime
from django.db.models.query_utils import Q
from django.contrib.admin.util import flatten_fieldsets

class ModelWithFlagsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }
    
class MatchAdmin(ModelWithFlagsAdmin):
    class PoolroomLocation(SimpleListFilter):
        title = _(u'球房所在区域')
        parameter_name = 'district'
    
        def lookups(self, request, model_admin):
            return ((poolroom['district'], poolroom['district']) for poolroom in Poolroom.objects.values('district').distinct()) 
    
        def queryset(self, request, queryset):
            if self.value() is None:
                return queryset
            return queryset.filter(poolroom__district=self.value())
        
    class MatchTimeFilter(SimpleListFilter):
        title = _(u'比赛所在月份')
        parameter_name = 'month'
        
        datefmt = '%Y-%m'
    
        def monthdelta(self, date, delta):
            m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
            if not m: m = 12
            d = min(date.day, [31,
                29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
            return date.replace(day=d,month=m, year=y)
        
        def lookups(self, request, model_admin):
            today = datetime.datetime.today()
            return ((self.monthdelta(today, 0-m).strftime(self.datefmt), self.monthdelta(today, 0-m).strftime(self.datefmt)) for m in range(0, 11)) 
    
        def queryset(self, request, queryset):
            if self.value() is None:
                return queryset
            datemonth = datetime.datetime.strptime(self.value(), self.datefmt)
            return queryset.filter(Q(starttime__gte=datemonth) & Q(starttime__lt=self.monthdelta(datemonth, 1)))
        
    list_filter = (
            ('flags', BitFieldListFilter),
            PoolroomLocation,
            MatchTimeFilter
            )
    save_as = True
    ordering = ('-starttime', '-id')

class PoolroomAdmin(ModelWithFlagsAdmin):
    list_filter = (
            ('flags', BitFieldListFilter),
            )
    def save_model(self, request, obj, form, change):
        # custom stuff here
        if ((obj.lat_baidu == 0 or obj.lng_baidu == 0) and (obj.lat != 0 and obj.lng != 0)) or \
            (obj.pk is not None and (form.fields['lat'] != obj.lat or form.fields['lng'] != obj.lng)):
            baiduLoc = gcj2bd(float(obj.lat), float(obj.lng))
            obj.lat_baidu = baiduLoc[0]
            obj.lng_baidu = baiduLoc[1]
            obj.location = (obj.lat, obj.lng)
        if (obj.location is None):
            obj.location = (obj.lat, obj.lng)
        obj.save()
        
    exclude = ['location', 'lat_baidu', 'lng_baidu']
        
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
            (_('Social Site info'), {'fields': ('get_nickname', 'site_name', 'gender', 'avatar',
                                                'access_token', 'expire_time', 
                                                'refresh_token')}),
        )
    form = CustomUserChangeForm
    list_display = UserAdmin.list_display + ('get_nickname', 'site_name', 'gender', 'cellphone')
    search_fields = UserAdmin.search_fields + ('get_nickname', )

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
    
class ImageAdmin(admin.ModelAdmin):
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
        return self.readonly_fields + ('userid', 'eventtype', 'message', 'receivedtime', 'reply', 'target')
    
class MembershipAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
class AssistantAppointmentAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if self.declared_fieldsets:
            fieldsets = flatten_fieldsets(self.declared_fieldsets)
            fieldsets.remove('state')
            return fieldsets
        else:
            return list(set(
                [field.name for field in self.opts.local_fields if field.name != 'state'] +
                [field.name for field in self.opts.local_many_to_many]
            ))
    
    def has_add_permission(self, request):
        # Nobody is allowed to add
        return False
    def has_delete_permission(self, request, obj=None):
        # Nobody is allowed to delete
        return False         
    
class AssistantUserAdmin(admin.ModelAdmin):
    raw_id_fields = ('assistant', 'user')
    
admin.site.register(Poolroom, PoolroomAdmin)
admin.site.register(PoolroomEquipment)
admin.site.register(Match, MatchAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(MatchEnroll)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(ChallengeApply, ChallengeApplyAdmin)
admin.site.register(PoolroomImage, ImageAdmin)
admin.site.register(PoolroomUser, PoolroomUserAdmin)
admin.site.register(PoolroomUserApply)
admin.site.register(Group)
admin.site.register(Coupon)
admin.site.register(WechatActivity, WechatActivityAdmin)
admin.site.register(Event)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Goods)
admin.site.register(Assistant, ModelWithFlagsAdmin)
admin.site.register(AssistantOffer, ModelWithFlagsAdmin)
admin.site.register(AssistantAppointment, AssistantAppointmentAdmin)
admin.site.register(AssistantImage, ImageAdmin)
admin.site.register(AssistantUser, AssistantUserAdmin)