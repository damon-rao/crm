from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)

from django.utils.safestring import mark_safe
# Create your models here.


class Customer(models.Model):
    '''客户表'''
    # blank是django admin的，null是数据库      help_text是提示
    name = models.CharField(max_length=32,blank=True,null=True,help_text='用户报名后，请改为真实姓名')
    qq = models.CharField(max_length=64,unique=True)
    qq_name = models.CharField(max_length=32)
    phone = models.CharField(max_length=64,blank=True,null=True)
    source_choices = ((0,'转介绍'),
                  (1,'qq群'),
                  (2,'百度推广'),
                  (3,"知乎"),
                  (4,'市场推广'),
                  )
    source = models.SmallIntegerField(choices=source_choices)
    referral_from=models.CharField(verbose_name='转介绍人',max_length=64,blank=True,null=True)
    consult_course=models.ForeignKey('Course',verbose_name='咨询课程',on_delete=models.CASCADE)
    content = models.TextField(verbose_name='咨询详情')
    tags=models.ManyToManyField('Tag',blank=True)
    consultant = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    memo = models.TextField(blank=True,null=True)#备忘录
    date = models.DateField(auto_now_add=True)
    status_choices = ((0,'未报名'),
                      (1,'已报名'),)
    status = models.SmallIntegerField(choices=status_choices,default=0)
    id_card=models.CharField(max_length=64,blank=True,null=True)
    email=models.EmailField(verbose_name='常用邮箱',max_length=64,blank=True,null=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '客户表'


class Tag(models.Model):
    name=models.CharField(unique=True,max_length=32)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '标签'

class CustomerFollowUp(models.Model):
    '''客户跟进'''
    customer = models.ForeignKey('Customer',on_delete=models.CASCADE)
    consultant = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    content = models.TextField(verbose_name='跟进内容')
    intention_choices = ((0,'一周内无报名计划'),
                         (1,'一个月内无报名计划'),
                         (2,'暂时无需求'),
                         (3,'已在其他机构报名'),
                         )
    intention=models.IntegerField(choices=intention_choices)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return '<%s:%s>'%(self.customer , self.intention)

    class Meta:
        verbose_name_plural = '跟进表'


class Course(models.Model):
    '''课程表'''
    name=models.CharField(max_length=32,unique=True)
    price=models.PositiveIntegerField()
    period=models.PositiveIntegerField(verbose_name='周期（月）')
    outline=models.TextField()
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '课程表'

class Branch(models.Model):
    '''校区'''
    name=models.CharField(max_length=128,unique=True)
    addr=models.CharField(max_length=128)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '校区表'


class ClassList(models.Model):
    '''班级表'''
    branch=models.ForeignKey('Branch', on_delete=models.CASCADE)
    course=models.ForeignKey('Course',on_delete=models.CASCADE)
    class_type_choices=((0,'面授班（脱产）'),
                        (1, '面授班（周末）'),
                        (2,'网络班')
                        )
    semester=models.PositiveIntegerField(verbose_name='学期')
    teacher=models.ManyToManyField('UserProfile')
    start_date=models.DateField(verbose_name='开班时间')
    send_date=models.DateField(verbose_name='结业时间',blank=True,null=True)
    contract=models.ForeignKey('ContractTemplate',blank=True,null=True,on_delete=models.CASCADE)


    def __str__(self):
        return '%s %s %s' %(self.branch,self.course,self.semester)

    class Meta:
        unique_together=('branch', 'course', 'semester')
        verbose_name_plural='班级表'

class CourseRecord(models.Model):
    '''上课记录'''
    from_class = models.ForeignKey('ClassList',verbose_name='班级',on_delete=models.CASCADE)
    day_num = models.PositiveIntegerField(verbose_name="第几节课(天)")
    teacher = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    has_homework=models.BooleanField(default=True)
    homework_title=models.CharField(max_length=128,blank=True,null=True)
    homework_conent=models.TextField(blank=True,null=True)
    outline=models.TextField(verbose_name='本节大纲')
    date=models.DateField(auto_now_add=True)

    def __str__(self):
        return '%s %s '%(self.from_class, self.day_num)

    class Meta:
        unique_together = ('from_class', 'day_num')
        verbose_name_plural='上课记录'

class StudyRecord(models.Model):
    '''学习记录'''
    student=models.ForeignKey('Enrollment',on_delete=models.CASCADE)
    course_record=models.ForeignKey('CourseRecord',on_delete=models.CASCADE)
    attendance_choices=((0,"已签到"),
                        (1,'迟到'),
                        (2,"缺勤"),
                        (3,'早退'),
                        )
    attendance=models.SmallIntegerField(choices=attendance_choices,default=0)
    score_choices=((100,'A+'),
                   (90,'A'),
                   (85,'B+'),
                   (80,'B'),
                   (75,'B-'),
                   (70,'C+'),
                   (60,'C'),
                   (40,'C-'),
                   (-50,'D'),
                   (-100,'COPY'),
                   (0,'N/A'),
                   )
    score=models.SmallIntegerField(choices=score_choices)
    meomo=models.TextField(blank=True,null=True)
    date=models.DateField(auto_now_add=True)
    def __str__(self):
        return '%s %s %s'%(self.student,self.course_record, self.score)

    class Meta:
        unique_together = ('student','course_record')
        verbose_name_plural = '学习记录'

class Enrollment(models.Model):
    '''报名表'''
    customer=models.ForeignKey('Customer',on_delete=models.CASCADE)
    enrolled_class=models.ForeignKey('ClassList',verbose_name='所报名班级',on_delete=models.CASCADE)
    consultant=models.ForeignKey('UserProfile',verbose_name='课程顾问',on_delete=models.CASCADE)
    contract_agreed=models.BooleanField(default=False,verbose_name='学院已同意合同条款')
    contract_approved=models.BooleanField(default=False,verbose_name='已审核')
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return '%s %s '%(self.customer,self.enrolled_class)
    class Meta:
        unique_together=('customer','enrolled_class')
        verbose_name_plural = '报名表'

class Payment(models.Model):
    '''缴费记录'''
    customer=models.ForeignKey('Customer',on_delete=models.CASCADE)
    course=models.ForeignKey('Course',verbose_name='所报课程',on_delete=models.CASCADE)
    amount=models.PositiveIntegerField(verbose_name='缴费数额',default=500)
    consultant = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s'%(self.customer,self.amount)

    class Meta:
        verbose_name_plural = '缴费记录'

class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        self.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self,email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_active = True
        user.is_admin = True
        user.save(using=self._db)
        return user

#PermissionsMixin显示权限
class UserProfile(AbstractBaseUser,PermissionsMixin):
    '''账号表'''
    password = models.CharField(('password'), max_length=128,help_text=mark_safe("<a href='password/'>点击修改密码</a>"))
    email=models.EmailField(
        max_length=255,
        verbose_name='email_address',
        unique=True,
        null=True,
    )
    # user=models.OneToOneField(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=32)
    roles=models.ManyToManyField('Role',blank=True)
    #是否激活，活跃。
    is_active = models.BooleanField(default=True)
    #是否是管理员
    is_admin = models.BooleanField(default=False)
    # 设置用户名
    USERNAME_FIELD='email'
    #创建用户时候，必须的字段
    REQUIRED_FIELDS=['name']
    objects = UserProfileManager()
    stu_account = models.ForeignKey("Customer", verbose_name="关联学员账号", blank=True, null=True,
                                    help_text="只有学员报名后方可为其创建账号",on_delete=models.CASCADE)

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin



class Role(models.Model):
    '''角色表'''
    name = models.CharField(max_length=32,unique=True)
    menus = models.ManyToManyField('Menu', blank=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = '角色表'


class Menu(models.Model):
    '''菜单表'''
    name=models.CharField(max_length=32)
    url_type_choices = ((0,'alias'),(1,'absolute_url'))
    url_type=models.SmallIntegerField(choices=url_type_choices,default=0)
    url_name=models.CharField(max_length=64)

    def __str__(self):
        return self.name

class ContractTemplate(models.Model):
    name=models.CharField('合同名称',max_length=64,unique=True)
    template=models.TextField()
    def __str__(self):
        return self.name