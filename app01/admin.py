from django.contrib import admin
from app01 import models
from django.shortcuts import render,redirect,HttpResponse

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    #设置列表显示的字段
    list_display = ('id', 'qq', 'source', 'consultant', 'content', "status", 'date')
    #过滤选项设置
    list_filter = ('source', 'consultant', 'date')
    #设置搜索
    search_fields = ('qq', 'name')
    #显示外键的详细信息
    raw_id_fields = ('consult_course',)
    #已选和未选数据展示（复选框 ）
    filter_horizontal = ('tags',)
    #设置可编辑字段
    list_editable = ('status',)
    #只读不能修改的字段
    # readonly_fields = ['qq','consultant']
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('email','name','is_active')

# `````````````````````````````````````````````````````````````
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.UserProfile
        fields = ('email', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.UserProfile
        fields = ('email', 'password', 'name', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_admin','is_active','is_staff')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('name','stu_account')}),
        ('Permissions', {'fields': ('is_admin','is_active','roles','user_permissions','groups')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups','user_permissions')

class CourseRecordAdmin(admin.ModelAdmin):
    '''上课记录'''
    list_display = ['from_class','day_num','teacher','has_homework','homework_title','date']
    list_filter = []

    def initialize_studyrecord(self, request, queryset):
        '''初始化学习记录'''
        print('self,request,queryset',self, request, queryset)
        if len(queryset)>1:
            return HttpResponse('只能选择一个')
            # enrollment关联着外键，_set反向查找拿到
        new_obj_list=[]
        for enrollment_obj in queryset[0].from_class.enrollment_set.all():
            print(enrollment_obj)
            # models.StudyRecord.objects.get_or_create(
            #     student=enrollment_obj,
            #     course_record=queryset[0],
            #     attendance=0,
            #     score=0,
            # )
            new_obj_list.append(models.StudyRecord(
                student=enrollment_obj,
                course_record=queryset[0],
                attendance=0,
                score=0,
            ))
            #之前用get_or_create避免的重复修改的问题，但是使用bulk_create避免不了，只能接受错误
        try:
            models.StudyRecord.objects.bulk_create(new_obj_list)#具有事务性，批量创建
        except Exception as e:
            return HttpResponse('批量修改失败，有学生已经有对应的学习记录')

            # ?course_record__id__exact =带上过滤的的值，跳转过去只显示指定的值
        return redirect('/admin/app01/studyrecord/?course_record__id__exact=%s'%queryset[0].id)

    initialize_studyrecord.short_description = "初始化所有学习记录"
    actions=['initialize_studyrecord',]

class StudyRecordAdmin(admin.ModelAdmin):
    list_display = ['student','course_record','attendance','score','date']
    list_filter = ['course_record','date']
    #字段可以在页面点击修改
    list_editable = ['attendance','score']

# Now register the new UserAdmin...
admin.site.register(models.StudyRecord, StudyRecordAdmin)
admin.site.register(models.CourseRecord, CourseRecordAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.Course)
admin.site.register(models.Customer,CustomerAdmin)
admin.site.register(models.ClassList)
admin.site.register(models.Enrollment)
admin.site.register(models.Branch)
admin.site.register(models.CustomerFollowUp)
admin.site.register(models.Payment)
admin.site.register(models.Role)
admin.site.register(models.Tag)
admin.site.register(models.Menu)
admin.site.register(models.ContractTemplate)