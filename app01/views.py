from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,HttpResponse
from app01 import forms,models
from django.db import IntegrityError
import random,string
from django.core.cache import cache
from CRM01 import settings
import os
@login_required
def index(req):
    return render(req, 'index.html')
@login_required
def customer_list(req):
    return render(req, 'sales/customers.html')

def enrollment(request,customer_id):
    '''报名流程'''
    msgs={}
    customer_obj=models.Customer.objects.get(id=customer_id)
    if request.method=='POST':
        #enroll_form是所有的数据
        enroll_form=forms.EnrollmentModelForm(request.POST)
        if enroll_form.is_valid():
            msg='''请将此链接发送给客户进行填写：
            http://localhost:8000/app01/customer/registration/{enroll_obj_id}/{random_str}'''
            try:
                enroll_form.cleaned_data['customer']=customer_obj
                enroll_obj=models.Enrollment.objects.create(**enroll_form.cleaned_data)
                random_str = ''.join(random.sample(string.ascii_lowercase + string.digits, 8))
                cache.set(enroll_obj.id, random_str, 3000)
                msgs['msg']=msg.format(enroll_obj_id=enroll_obj.id,random_str=random_str)
            except IntegrityError as e:
                enroll_obj = models.Enrollment.objects.get(customer_id=customer_obj.id,
                                                           enrolled_class_id=enroll_form.cleaned_data[
                                                               "enrolled_class"].id)
                if enroll_obj.contract_agreed==True:
                    return redirect("/app01/contract_review/%s/"%enroll_obj.id)

                enroll_form.add_error('__all__','该用户此条报名信息已存在')
                # 拿到一個八位的小寫字母加數字的隨機字符串
                random_str=''.join(random.sample(string.ascii_lowercase+string.digits,8))
                # 設置cashe，以及過期時間
                cache.set(enroll_obj.id,random_str,3000)
                msgs['msg'] = msg.format(enroll_obj_id=enroll_obj.id,random_str=random_str)
    else:
        enroll_form=forms.EnrollmentModelForm()
    return render(request,'sales/enrollment.html',
                  {'enroll_form':enroll_form,'customer_obj':customer_obj,'msgs':msgs})



def stu_registration(request,enroll_id,random_str):
    if cache.get(enroll_id)==random_str:
        enroll_obj=models.Enrollment.objects.get(id=enroll_id)
        if request.method=='POST':
            # 判断如果是ajax请求(传照片的)
            if request.is_ajax():
                # print('ajax',request.FILES)
                enrolled_data_dir='%s/%s'%(settings.ENROLLED_DATA,enroll_id)
                #判断路劲是否存在
                if not os.path.exists(enrolled_data_dir):
                    # makedirs是层级创建，exist_ok=True上级存在就不会创建了
                    os.makedirs(enrolled_data_dir,exist_ok=True)
                for k,file_obj in request.FILES.items():
                    with open('%s/%s'%(enrolled_data_dir,file_obj.name),'wb')as f:
                        for chunk in file_obj.chunks():
                            f.write(chunk)
                return HttpResponse('success')

            customer_form = forms.CustomerForm(request.POST, instance=enroll_obj.customer)
            if customer_form.is_valid():
                # 保存
                customer_form.save()
                # contract_agreed改成同意
                enroll_obj.contract_agreed = True
                enroll_obj.save()
                return render(request, 'sales/stu_registration.html', {'status':1})
        else:
            if enroll_obj.contract_agreed==True:
                status=1
            else:
                status=0
            customer_form=forms.CustomerForm(instance=enroll_obj.customer)

            return render(request, 'sales/stu_registration.html',
                      {'customer_form':customer_form, 'enroll_obj':enroll_obj,'status':status})
    else:
        return HttpResponse('链接已过期')

def contract_review(request,enroll_id):
    enroll_obj=models.Enrollment.objects.get(id=enroll_id)
    enroll_form=forms.EnrollmentModelForm(instance=enroll_obj)
    customer_form=forms.CustomerForm(instance=enroll_obj.customer)
    return render(request,'sales/contract_review.html',
                  {'enroll_id':enroll_id,'enroll_form':enroll_form,'customer_form':customer_form})

def enrolled_rejection(request,enroll_id):
    enroll_obj=models.Enrollment.objects.get(id=enroll_id)
    enroll_obj.contract_agreed=False
    enroll_obj.customer.status=0
    enroll_obj.customer.save()
    enroll_obj.save()
    return redirect('/customer/%s/enrollment/'%enroll_obj.customer.id)


def payment(request,enroll_id):
    enroll_obj=models.Enrollment.objects.get(id=enroll_id)
    errors=[]
    if request.method=='POST':
        payment_amount=request.POST.get('amount')
        # print('payment_amount',payment_amount)
        if payment_amount:
            if int(payment_amount)< 500:
                errors.append('金额必须大于500')
            else:
                payment_obj=models.Payment.objects.create(
                    customer=enroll_obj.customer,
                    course=enroll_obj.enrolled_class.course,
                    amount=payment_amount,
                    consultant=enroll_obj.consultant,
                )
                enroll_obj.customer.status = 1
                enroll_obj.customer.save()
                return redirect("/app01/customer/")
        else:
            errors.append('金额必须大于500')
    return render(request,'sales/payment.html',{'enroll_obj':enroll_obj,'errors':errors})

