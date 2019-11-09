from django.db.models import Q
def table_sort(req,objs):
    orderby_key=req.GET.get('o')
    if orderby_key:
        res = objs.order_by(orderby_key)
        if orderby_key.startswith('-'):
            orderby_key=orderby_key.strip('-')
        else:
            orderby_key='-%s'%orderby_key
    else:
        res=objs
    return res,orderby_key

def table_search(req,admin_class,queryset):
    search_key=req.GET.get('_q','') #拿到提交的_q数据（_q是前端name=_q定义的名字）
    q_obj=Q()
    q_obj.connector='OR' # or 或判断
    for column in admin_class.search_fields:#在kingadmin的search_fields中循环出设置的搜索数据
        q_obj.children.append(('%s__contains'%column,search_key))
    res=queryset.filter(q_obj)
    return res

