from django import template
from django.utils.safestring import mark_safe
import datetime
from django.core.exceptions import FieldDoesNotExist


register = template.Library()

@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name_plural  # 显示的是models走之前设置的verbose_name的中文名
    # return admin_class.model._meta.model_name  # 显示英文表名

# @register.simple_tag
# def get_query_sets(admin_class):
#     return admin_class.model.objects.all()
#obj拿到所有字段对象
@register.simple_tag
# '''展示字段跟value'''
def build_table_row(request,obj,admin_class):
    row_ele=''

    for index,column in enumerate(admin_class.list_display) :#要展示的每个字段名字,跟字段的索引index（enumerate的作用）
        try:
            field_obj = admin_class.model._meta.get_field(column)#从admin_class.model(类customer等..)取column字段的对象app01.Customer.qq
            if field_obj.choices:#判断是否有choices字段,.choices得到的是‘(1,未报名)’之类的数据,无，得到个[]
                #用如下方法使choice显示的不是序号，而是详细信息
                column_data = getattr(obj,'get_%s_display'%column)()# get_**_display得到的是choices对应的详细信息而不是序号
            else:
                # 相当于obj.字段   但是这里的字段名是str所以我们用了getattr方法
                column_data=getattr(obj, column)
            if type(column_data).__name__ == 'datetime':
                column_data = column_data.strftime('%Y-%m-%d %H:%M:%S')

            if index == 0:
                # print(request.path)
                column_data = "<a href='{request_path}{obj_id}/change/'>{data}</a>".format(request_path=request.path,
                                                                                       obj_id=obj.id,
                                                                                          data=column_data)
        except FieldDoesNotExist as e:
                if hasattr(admin_class,column):
                    column_func=getattr(admin_class,column)
                    #定制方法
                    admin_class.instance = obj#king_admin利用obj取得id
                    admin_class.request = request
                    column_data=column_func()
        row_ele += '<td>%s</td>'%column_data
    # 因为返回值有html标签，所以需要mark_safe
    return mark_safe(row_ele)
#过滤器
@register.simple_tag
# 过滤功能
def build_filter_ele(filter_column,admin_class):
    '''list_filter,主要是时间过滤麻烦'''
    filter_ele = "<select name='%s'>" % filter_column
    column_obj = admin_class.model._meta.get_field(filter_column)

    try:#date没有get_choices()这个方法，所以会报错，这里接收这个错误（其他字段都有这个方法）
        for choice in column_obj.get_choices():#get_choices()能获得choices跟外键 的值
         #choice ('', '---------')(0, '转介绍')
            selected=''#字段名 in 所选择的字段名egg：（date，source）
            if filter_column in admin_class.filter_conditions: #该字段 为 所选择的过滤 字段
                # 字段的值 = 所选字段的值
                                                #filter_conditions={'source':'1'}类似这种
                if str(choice[0]) == admin_class.filter_conditions.get(filter_column):#当前值被选中
                   #1=1
                    selected='selected'
            option = "<option value='%s'%s>%s</option>" % (choice[0],selected,choice[1])
            filter_ele+=option
            #choice为date的时候
    except AttributeError as e:
        # print('err',e)
        #用字符串拼接的方式，gte大等于  lt小于
        filter_ele = "<select name='%s__gte'>" % filter_column
        if column_obj.get_internal_type()in('DateField','DateTimeField'):
            time_obj=datetime.datetime.now()
            time_list=[
                ('','----'),
                (time_obj,'Today'),
                (time_obj-datetime.timedelta(7),'七天内'),
                (time_obj.replace(day=1),'本月'),
                (time_obj-datetime.timedelta(90),'三个月内'),
                (time_obj.replace(month=1,day=1),'一年内'),
                ('','All'),
            ]

            for i in time_list:
                selected = ''  # 字段名 in 所选择的字段名egg：（date，source）
                time_str=''if not i[0] else "%s-%s-%s"%(i[0].year,i[0].month,i[0].day)
                if '%s__gte'%filter_column in admin_class.filter_conditions:  # 该字段 为 所选择的过滤 字段
                    # 字段的值 = 所选字段的值
                    if time_str == admin_class.filter_conditions.get('%s__gte'%filter_column):  # 当前值被选中
                        selected = 'selected'
                option = "<option value='%s'%s>%s</option>" %(time_str,selected,i[1])
                filter_ele += option
    filter_ele += '</select>'
    return mark_safe(filter_ele)

# @register.simple_tag
# def render_page_btn(queryset,admin_class):
#     filters=''
#     for k,v in admin_class.filter_conditions.items():
#         filters+='&%s=%s'%(k,v)
#     ele='''      '''
#
#     for i in queryset.paginator.page_range:
#         if i<3 or i >queryset.paginator.num_pages-2:
#             print(queryset.paginator.page_range)
#             active = ''
#             if queryset.number == i:
#                 active = 'active'
#                 # 把过滤条件添加到href中
#             p_ele = '''<li class=%s><a href="?_page=%s%s">%s</span></a></li>''' % (active, i, filters, i)
#             ele += p_ele
#
#         if abs(queryset.number-i)<2 and i>2 and i <queryset.paginator.num_pages-1:
#             active=''
#             if queryset.number==i:
#                 active='active'
#                 #把过滤条件添加到href中
#             p_ele= '''<li class=%s><a href="?_page=%s%s">%s</span></a></li>'''%(active,i,filters,i)
#             ele+=p_ele
#     return mark_safe(ele)

@register.simple_tag
def render_dot(queryset, admin_class, previous_orderby,search_text):
    '''分页'''
    filters = ''
    for k, v in admin_class.filter_conditions.items():
        filters += '&%s=%s' % (k, v)
    ele = '''      '''
    add_dot=False#设置个标志位
    for i in queryset.paginator.page_range:

        if i < 3 or i > queryset.paginator.num_pages - 2:
            # print(queryset.paginator.page_range)
            active = ''
            if queryset.number == i:
                active = 'active'
                # 把过滤条件添加到href中
            p_ele = '''<li class=%s><a href="?_page=%s%s&o=%s&_q=%s">%s</span></a></li>'''\
                    % (active, i, filters,previous_orderby,search_text,i)
            ele += p_ele

        elif abs(queryset.number - i) < 2 and i > 2 and i < queryset.paginator.num_pages - 1:
            active = ''
            add_dot = False
            if queryset.number == i:
                active = 'active'
                # 把过滤条件添加到href中
            p_ele = '''<li class=%s><a href="?_page=%s%s&o=%s&_q=%s">%s</span></a></li>''' % (active, i, filters,previous_orderby,search_text,i)
            ele += p_ele
        else:
            if add_dot==False:
                p_ele='''<li><a>...</a></li>'''
                ele += p_ele
                #添加完..后吧标志位改动，但是后面也会有需要省略成..的页码，在elif里添加修改标志位
                add_dot=True
    return mark_safe(ele)

@register.simple_tag
def get_message(admin_class):
    filters = ''
    for k, v in admin_class.filter_conditions.items():
        filters += '&%s=%s' % (k, v)
    return filters

@register.simple_tag
def get_previous_orderby(previous_orderby):
    previous_orderby='&o=%s'% previous_orderby
    return previous_orderby
@register.simple_tag
def get_search(search_text):
    search_text='&_q=%s'%search_text
    return search_text

@register.simple_tag
def build_table_header_column(column,orderby_key,admin_class,search_text):
    '''orderby排序'''

    filters = ''
    for k, v in admin_class.filter_conditions.items():
        filters += '&%s=%s' % (k, v)
    ele='''<th><a href="?{filters}&o={orderby_key}&_q={search_text}">{column}</a>{sort_icon}</th>'''
    if orderby_key:
        if orderby_key.startswith('-'):
            sort_icon='''<span class="glyphicon glyphicon-chevron-up"></span>'''
        else:
            sort_icon='''<span class="glyphicon glyphicon-chevron-down"></span>'''
        if orderby_key.strip("-")==column:
            orderby_key=orderby_key
        else:
            orderby_key=column
            sort_icon=''
    else:#没有排序
        orderby_key = column
        sort_icon=''
    try:
        verbose_column=admin_class.model._meta.get_field(column).verbose_name
    except FieldDoesNotExist as e:
        verbose_column=getattr(admin_class,column).display_name
        #到我们加的enroll时候，改成不可点击排序的，不然会报错（其他heard点击会排序）
        ele = '''<th><a href='javascript:void(0)'>{column}</a></th>'''.format(column=verbose_column)
        return mark_safe(ele)
    ele = ele.format(orderby_key=orderby_key, column=verbose_column,search_text=search_text,sort_icon=sort_icon,filters=filters)
    return mark_safe(ele)

@register.simple_tag
def get_title_name(admin_class):
    return admin_class.model._meta.verbose_name_plural

@register.simple_tag
def get_action_verbose_name(admin_class,action):
    action_func=getattr(admin_class,action)
    #如果没有display_name方法，就返回action
    return action_func.display_name if hasattr(action_func,'display_name') else action

