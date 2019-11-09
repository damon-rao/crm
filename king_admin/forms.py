from django.forms import forms,ModelForm
from app01 import models
from django.forms import ValidationError
# from django.utils.translation import ugettext as _

class CustomerModelForm(ModelForm):
    class Meta:
        model=models.Customer
        fields='__all__'

def create_model_form(request,admin_class):
    '''生成动态的model_form'''
    # 加入新的class属性
    def __new__(cls, *args, **kwargs):
        # cls.base_fields得到一个有序的字典{qq.obj}
        # 遍历，把每个obj加上form-control
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            #判断是否在添加的可读字段中
            if not hasattr(admin_class,'add_form'):
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled'] = 'disabled'
        return ModelForm.__new__(cls)#相当于继承了modelform其他放法


    def default_clean(self):
        '''给所有的form加一个默认的clean验证'''
        print('instance',self.instance.id )
        error_list=[]
        if self.instance.id: # 这是个修改的表单,add没有id
            for field in admin_class.readonly_fields:
                field_val=getattr(self.instance,field)
                field_val_from_frontend=self.cleaned_data.get(field)
                if field_val != field_val_from_frontend:
                    error_list.append(ValidationError(
                        ('傻屌还想黑我Field %(field)s is readonly,data should be %(val)s'),
                        code='invalid',
                        params={'field': field, 'val': field_val},
                    ))

            self.ValidationError=ValidationError
            response=admin_class.default_form_validition(self)
            if response:
                error_list.append(response)

            if error_list:
                raise ValidationError(error_list )

    class Meta:
        model=admin_class.model
        fields='__all__'
    attrs={'Meta':Meta}
    #创建了一个类model_form_class
    model_form_class = type("DynamicModelForm",(ModelForm,),attrs)
    setattr(model_form_class,'__new__',__new__)
    setattr(model_form_class,'clean',default_clean)

    return model_form_class