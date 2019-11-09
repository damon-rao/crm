from django.shortcuts import render,redirect
from king_admin import king_admin
from django.core.paginator import Paginator
from king_admin.utils import table_sort,table_search
from king_admin.forms import create_model_form
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def index(req):
    return render(req, 'king_admin/table_index.html',{'table_list':king_admin.enabled_admin})

@login_required
def get_filter_result(req,queryset):
    filter_conditions={}
    a=req.GET#<QueryDict: {'source': ['0'], 'consultant': [''], 'status': [''], 'date__gte': ['']}>
    keywords=['_page','o','_q']
    for k ,v in req.GET.items():
        if k in keywords: #设置分页后_page=1 也会被传入过滤条件，所以，跳过page
            continue
        if v:
            filter_conditions[k]=v#{'source': '4', 'consultant': '1'}
    return queryset.filter(**filter_conditions).order_by('-id'),filter_conditions

@login_required
def display_table_objs(req,app_name,table_name):
    '''提供过滤后的数据'''
    admin_class=king_admin.enabled_admin[app_name][table_name]
    #action全选编辑选项，最后把selected_objs传到kingadmin···········
    if req.method=='POST':  #action来了，tables页面没有其他的post提交。
        selected_ids=req.POST.get('selected_ids')
        action=req.POST.get('action')
        if selected_ids:                                    #是个字符串['22,21,20']，变成列表
            selected_objs=admin_class.model.objects.filter(id__in=selected_ids.split(','))
        else:
            raise KeyError('No objeect selected')
        if hasattr(admin_class,action):#判断是否有action方法
            action_func=getattr(admin_class,action)
            req._admin_action=action#为第二次post确认删除提交准备的action，，，然后由king_admin传到前端的隐藏input
            #传到king_admin的数据
            return action_func(admin_class, req, selected_objs)

    queryset=admin_class.model.objects.all()#<QuerySet [<Customer: 23423451>, <Customer: 54634451>, <Customer: 234234234>]>
    queryset,filter_conditions=get_filter_result(req,queryset)#过滤后的结果
    queryset=table_search(req,admin_class,queryset)

    queryset,orderby_key=table_sort(req,queryset)
    admin_class.filter_conditions=filter_conditions
    #·······分页······
    paginator = Paginator(queryset,3)  # Show num contacts per page
    page = req.GET.get('_page')#拿第几页

    queryset = paginator.get_page(page)#这个页码的内容
    return render(req,'king_admin/table_objs.html',{"queryset":queryset,
                                                    'admin_class':admin_class,
                                                    'orderby_key':orderby_key,
                                                    'previous_orderby':req.GET.get('o', ''),
                                                    'search_text':req.GET.get('_q','')
                                                    })

@login_required
def table_obj_change(request,app_name,table_name,obj_id):
    '''修改用户'''
    admin_class=king_admin.enabled_admin[app_name][table_name]
    model_form_class = create_model_form(request, admin_class)
    obj = admin_class.model.objects.get(id=obj_id)
    if request.method=='POST':

        #form_obj所有的数据，然后传到前端取循环展示
        form_obj = model_form_class(request.POST,instance=obj)#更新，如果没instance=obj,前端的input都没有值
        if form_obj.is_valid():#验证
            form_obj.save()
    else:
        form_obj=model_form_class(instance=obj) #instance实例
    return render(request,'king_admin/table_obj_change.html',{'form_obj':form_obj, 'app_name': app_name,
                                                            'table_name': table_name,})

@login_required
def table_obj_add(request,app_name,table_name):
    '''添加用户'''
    admin_class = king_admin.enabled_admin[app_name][table_name]
    admin_class.add_form=True
    model_form_class = create_model_form(request, admin_class)
    if request.method == 'POST':
        form_obj = model_form_class(request.POST)  # 更新
        if form_obj.is_valid():  # 验证
            form_obj.save()
            return redirect(request.path.replace('/add/','/'))
    else:
        form_obj = model_form_class()
    return render(request, 'king_admin/table_obj_add.html', {'form_obj': form_obj,
                                                             'app_name': app_name,
                                                             'table_name': table_name,
                                                             }
                  )

@login_required
def table_obj_delete(request,app_name,table_name,obj_id):
    admin_class = king_admin.enabled_admin[app_name][table_name]
    obj=admin_class.model.objects.get(id=obj_id)
    if request.method=='POST':
        obj.delete()
        return redirect("/%s/%s/" % (app_name, table_name))
    return render(request,'king_admin/table_obj_delete.html',{'obj':obj,
                                                              "admin_class":admin_class,
                                                                'app_name':app_name,
                                                                'table_name':table_name,
                                                                })

@login_required
def password_reset(request,app_name,table_name,obj_id):
    errors={}
    admin_class=king_admin.enabled_admin[app_name][table_name]
    model_form_class = create_model_form(request, admin_class)
    obj = admin_class.model.objects.get(id=obj_id)
    if request.method=='POST':
        password1=request.POST.get('password1')
        password2=request.POST.get('password2')
        if password1==password2:
            if len( password1)>5:
                obj.set_password(password1)#设置新的密码
                obj.save()
                return redirect(request.path.rstrip('password/')) #路径除去password就是change的路径
            else:
                errors['password-errors']='password is too sort'
        else:
            errors['password-errors']='password are not the same'

    return render(request,'king_admin/password_reset.html',{'obj':obj,'errors':errors})