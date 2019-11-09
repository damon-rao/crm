

from django.urls import path,re_path
from app01 import views

urlpatterns = [
    path('index/', views.index, name="sales_index"),
    re_path('customer/(\d+)/enrollment', views.enrollment, name="enrollment"),
    re_path('app01/customer/registration/(\d+)/(\w+)', views.stu_registration, name="stu_registration"),
    re_path('app01/contract_review/(\d+)', views.contract_review, name="contract_review"),
    re_path('app01/payment/(\d+)', views.payment, name="payment"),
    re_path('app01/enrolled_rejection/(\d+)', views.enrolled_rejection, name="enrolled_rejection"),
    path('customer/', views.customer_list, name='customer_list'),


]
