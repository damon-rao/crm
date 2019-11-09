

from django.urls import path
from student import views

urlpatterns = [

    path('student',views.stu_my_classes,name='stu_my_classes' ),
]
