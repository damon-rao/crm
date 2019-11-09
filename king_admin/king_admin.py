from app01 import models
from django.shortcuts import render,redirect,HttpResponse
from django.shortcuts  import render,redirect
enabled_admin={}

class BaseAdmin(object):
    list_display=[]
    list_filter=[]
    search_fields=[]
    readonly_fields = []
    readonly_table=False

    action=['delete_selected_objs',]

    def delete_selected_objs(self,request,querysets):
        print('self,requst,queryset',self,request,querysets)
        app_name=self.model._meta.app_label
        table_name=self.model._meta.model_name
        #之前这里写繁荣request.method==post,结果一点击go，没再次确认就直接删除了，所以换为
        # delete中隐藏的input来确定
        if request.POST.get('delete_confir') == 'yes':
            querysets.delete()
            return redirect('/%s/%s/'%(app_name,table_name))
        selected_ids='.'.join([str(i.id) for i in querysets])
        return render(request,'king_admin/table_obj_delete.html',{
            #这里的值为views传来的，self就是admin_class,querysets就是selected_objs
                                    "admin_class": self,
                                    'app_name': app_name,
                                    'table_name': table_name,
                                    'selected_ids':selected_ids,
                                    'action':request._admin_action,
        })
    def default_form_validition(self):
        '''自定义表单验证，相当于form的clean方法'''
        pass
    # 自定制名字
    delete_selected_objs.display_name='老朽给你全删了，ok？'

class CustomerAdmin(BaseAdmin):
    list_display = ['id','qq','name','source','consultant','consult_course','date','status','enroll']
    list_filter = ['source','consultant','status','date']
    search_fields = ['qq','name',"consultant__name"] #consultant字段是外键，所以设置成consultant__name，可以展示
   #不可修改的字段
    readonly_fields = ["qq", "consultant"]
    #自定制名字
    action = ['delete_selected_objs','test']
    readonly_table = True
    def test(self,request,querysets):
        print('test')
    test.display_name='无返回值报错，别点我'

    def default_form_validition(self):
        consult_content=self.cleaned_data.get('content')
        if len(consult_content)<5:
            return self.ValidationError(
                ('Field %(field)s长度不得低于5'),
                code = 'invalid',
                 params = {'field': 'content',},)

    def enroll(self):
        print('enroll',self.instance)
        if self.instance.status==0:
            link_name='报名'
        else:
            link_name='报名新课程'
        return '''<a href='/app01/customer/%s/enrollment/'>%s</a>'''%(self.instance.id,link_name)
    enroll.display_name='报名连接(点击报名)'
class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ('customer', 'consultant','content', 'date')
    list_filter = ['customer']
    search_fields = ['customer__name', 'consultant__name']

class UserProfileAdmin(BaseAdmin):
    list_display = ('email', 'name', 'roles')
    readonly_fields=('password',)
    filter_horizontal = ('groups', 'user_permissions')

def register(model_class,admin_class=None):
    if model_class._meta.app_label not in enabled_admin:
        enabled_admin[model_class._meta.app_label] = {}  #{'appname':{}}
    #相当于加了个新属性
    admin_class.model = model_class #绑定model对象和admin类
    enabled_admin[model_class._meta.app_label][model_class._meta.model_name] = admin_class

class CourseRecordAdmin(BaseAdmin):
    '''上课记录'''
    list_display = ['from_class','day_num','teacher','has_homework','homework_title','date']
    list_filter= ['from_class','day_num']

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
        return redirect('/app01/studyrecord/?course_record__id__exact=%s'%queryset[0].id)

    initialize_studyrecord.display_name = "初始化所有学习记录"
    action=['initialize_studyrecord',]

class StudyRecordAdmin(BaseAdmin):
    list_display = ['student','course_record','attendance','score','date']
    list_filter = ['course_record','date']
    #这里用不了
    list_editable = ['attendance','score']

register(models.Customer,CustomerAdmin)
register(models.CustomerFollowUp,CustomerFollowUpAdmin)
register(models.UserProfile,UserProfileAdmin)
register(models.CourseRecord,CourseRecordAdmin)
register(models.StudyRecord,StudyRecordAdmin)

#enabled_admin= {'app01': {'customer': <class 'king_admin.king_admin.CustomerAdmin'>}}
#               {'app01': {'customer': <class 'king_admin.king_admin.CustomerAdmin'>, 'customerfollowup': <class 'king_admin.king_admin.CustomerFollowUpAdmin'>}}