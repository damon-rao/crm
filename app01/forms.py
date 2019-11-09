from django.forms import ModelForm
from app01 import models

class EnrollmentModelForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        '''添加属性'''
        for field_name,field_obj in cls.base_fields.items():
            #每个字段添加属性
            field_obj.widget.attrs['class']='form-control'
        return ModelForm.__new__(cls)

    class Meta:
        model=models.Enrollment
        fields=['enrolled_class','consultant']

class  CustomerForm(ModelForm):
    def __new__(cls,*args,**kwargs):
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class']='form-control'
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'

        return ModelForm.__new__(cls)
    def clean_qq(self):
        #对比前端跟数据库值是否一致，防止黑客修改
        if self.instance.qq!=self.cleaned_data['qq']:
            self.add_error('qq', '傻逼你还想黑我fuck')
        #数据库值一致，返回值
        return self.cleaned_data['qq']

    class Meta:
        model = models.Customer
        fields = "__all__"
        # 取反
        exclude = ['tags','content','memo','status','referral_from','consult_course',]
        readonly_fields=['qq','customer','source']

class PaymentForm(ModelForm):
    class Meta:
        model=models.Payment
        fields='__all__'