from django.shortcuts import render

# Create your views here.
def stu_my_classes(request):
    return render(request,'students/student_index.html')