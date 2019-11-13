#_author: hasee
#date: 2019/8/14
from django.utils.safestring import mark_safe
from django import template
from django.utils.timezone import datetime,timedelta
from django.core.exceptions import FieldDoesNotExist
register=template.Library()


@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()

@register.simple_tag
def build_table_row(request,obj,admin_class):
    row_ele=''
    for index,column in enumerate(admin_class.list_display):
        try:
            field_obj=obj._meta.get_field(column)
            if field_obj.choices:
                column_data=getattr(obj,'get_%s_display'%(column))()
            else:
                column_data=getattr(obj,column)
            if type(column_data).__name__ == 'datetime':
                column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")
            if index==0: #add a tag 开图跳转到修改页
                column_data="<a href='{request_path}{obj_id}/change/'>{data}</a>".format(request_path=request.path,obj_id=obj.id,data=column_data)
        except FieldDoesNotExist as e:
            if hasattr(admin_class,column):
                column_func=getattr(admin_class,column)
                admin_class.instance=obj
                admin_class.request=request
                column_data=column_func()
        row_ele+='<td>%s</td>'% column_data
    return mark_safe(row_ele)

@register.simple_tag
def build_table_header_column(column,orderby_key,filter_conditions,admin_class):
    filters = ''
    for k, v in filter_conditions.items():
        filters += '&%s=%s' % (k, v)
    # ele='''< th > < a href = "?o={orderby_key}" > {column} < / a > < / th >'''
    ele='''<th><a href="?{filters}&o={orderby_key}">{column}</a>
    {sort_icon}
    </th>'''
    if orderby_key:
        if orderby_key.startswith('-'):
            sort_icon = '''<span class="glyphicon glyphicon-chevron-down" aria-hidden="true"></span>'''
        else:
            sort_icon = '''<span class="glyphicon glyphicon-chevron-up" aria-hidden="true"></span>'''
        if orderby_key.strip('-') == column:  # 排序的就是这个字段
            orderby_key=orderby_key
        else:
            orderby_key=column
            sort_icon = ''
    else: #没有排序
        orderby_key=column
        sort_icon=''
    try:
        column_verbose_name=admin_class.model._meta.get_field(column).verbose_name.upper()
    except FieldDoesNotExist as e:
        column_verbose_name=getattr(admin_class,column).display_name.upper()
        ele = '''<th><a href="javascript:void(0);">{column}</a></th>'''.format(column=column_verbose_name)
        return mark_safe(ele)
    ele=ele.format(orderby_key=orderby_key,column=column_verbose_name,sort_icon=sort_icon,filters=filters)
    return mark_safe(ele)

@register.simple_tag
def build_paginators(query_sets,filter_conditions,previous_orderby,search_text):
    #不再一下只返回一个小标签了，而是把整个分页当成一个整体
    page_btns=''
    filters=''
    for k,v in filter_conditions.items():
        filters+='&%s=%s'%(k,v)
    add_dot_ele=False
    for page_num in query_sets.paginator.page_range:
        if page_num<3 or page_num>query_sets.paginator.num_pages-2 or abs(query_sets.number - page_num) <= 1:#代表最前和最后2页
            ele_class = ""
            if query_sets.number == page_num:
                add_dot_ele = False
                ele_class = "active"
            page_btns += '''<li class="%s"><a href="?page=%s%s&o=%s&_q=%s">%s</a></li>''' % (
            ele_class, page_num, filters,previous_orderby,search_text,page_num)
        # elif abs(query_sets.number - page_num) <= 1: #判断前后每一页 一起2页
        #         ele_class = ""
        #         add_dot_ele = False
        #         if query_sets.number == page_num:
        #             ele_class = "active"
        #         ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, page_num, filters, page_num)
        else:
            if add_dot_ele==False:
                page_btns += '<li><a>...</a></li>'
                added_dot_ele = True

    return mark_safe(page_btns)

@register.simple_tag
def render_page_ele(loop_counter,query_sets,filter_conditions):
    filters=''
    for k,v in filter_conditions.items():
        filters+='&%s=%s'%(k,v)
    if loop_counter<3 or loop_counter>query_sets.paginator.num_pages-2:#代表前2和最后2页
        ele_class = ""
        if query_sets.number == loop_counter:
            ele_class = "active"
        ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' %(ele_class,loop_counter,filters,loop_counter)
        return mark_safe(ele)

    if abs(query_sets.number - loop_counter) <= 1:
        ele_class = ""
        if query_sets.number == loop_counter:
            ele_class = "active"
        ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' %(ele_class,loop_counter,filters,loop_counter)
        return mark_safe(ele)
    return ''

@register.simple_tag
def render_filter_ele(filter_field,admin_class,filter_condtions):
    # select_ele = '''<select class="form-control" name='%s' ><option value=''>----</option>''' %filter_field
    select_ele = '''<select class="form-control" name='{filter_field}' ><option value=''>----</option>'''
    field_obj = admin_class.model._meta.get_field(filter_field)
    if field_obj.choices:
        selected = ''
        for choice_item in field_obj.choices:
            print("choice",choice_item,filter_condtions.get(filter_field),type(filter_condtions.get(filter_field)))
            if filter_condtions.get(filter_field) == str(choice_item[0]):
                selected ="selected"

            select_ele += '''<option value='%s' %s>%s</option>''' %(choice_item[0],selected,choice_item[1])
            selected =''

    if type(field_obj).__name__ == "ForeignKey":
        selected = ''
        for choice_item in field_obj.get_choices()[1:]:
            if filter_condtions.get(filter_field) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value='%s' %s>%s</option>''' %(choice_item[0],selected,choice_item[1])
            selected = ''
    if type(field_obj).__name__ in ['DateTimeField','DateField']:
        date_els=[]
        today_ele=datetime.now().date()
        date_els.append(['今天', datetime.now().date()])
        date_els.append(["昨天", today_ele - timedelta(days=1)])
        date_els.append(["近7天", today_ele - timedelta(days=7)])
        date_els.append(["本月", today_ele.replace(day=1)])
        date_els.append(["近30天", today_ele - timedelta(days=30)])
        date_els.append(["近90天", today_ele - timedelta(days=90)])
        date_els.append(["近180天", today_ele - timedelta(days=180)])
        date_els.append(["本年", today_ele.replace(month=1, day=1)])
        date_els.append(["近一年", today_ele - timedelta(days=365)])
        selected = ''
        for item in date_els:
            select_ele += '''<option value='%s' %s>%s</option>''' % (item[1], selected, item[0])
        filter_field_name = '%s__gte' % filter_field
    else:
        filter_field_name = filter_field
    select_ele += "</select>"
    select_ele=select_ele.format(filter_field=filter_field_name)
    return mark_safe(select_ele)

@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_m2m_obj_list(admin_class,field,form_obj):
   #     干的是返回tag所有数据
    field_obj=getattr(admin_class.model,field.name) #表结构对象的某个字段
    all_obj_list=field_obj.rel.model.objects.all()
    if form_obj.instance.id:
        obj_instance_field =getattr(form_obj.instance,field.name) #单挑数据的对象中的某个字段
        selected_obj_list=obj_instance_field.all()
    else:  #代表这是在创建新的一条记录
        return all_obj_list
    standby_obj_list=[]
    for obj in all_obj_list:
        if obj not in selected_obj_list:
            standby_obj_list.append(obj)
    return standby_obj_list

@register.simple_tag
def get_m2m_selected_obj_list(form_obj,field):
    #返回已选择的m2m数据
    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance,field.name)
        return field_obj.all()

@register.simple_tag
def print_obj_methods(obj):
    print(1)

@register.simple_tag
def display_obj_related(objs):  #把对象及所有相关联的数据取出来
    if objs:
        model_class=objs[0]._meta.model
        mode_name=objs[0]._meta.model_name
        return mark_safe(recursive_related_objs_lookup(objs))

def recursive_related_objs_lookup(objs):
    # model_name=objs[0]._meta.model_name
    ul_ele='<ul>'
    for obj in objs:
        li_ele='''<li>%s:%s</li>'''%(obj._meta.verbose_name,obj.__str__().strip('<>'))
        ul_ele+=li_ele
        for m2m_field in obj._meta.local_many_to_many:
            sub_ul_ele='<ul>'
            m2m_field_obj=getattr(obj,m2m_field.name)#getattr(customer, 'tags')
            for o in m2m_field_obj.select_related():# customer.tags.all()
                li_ele = '''<li>%s:%s</li>''' % (m2m_field.verbose_name, o.__str__().strip('<>'))
                sub_ul_ele+=li_ele
            sub_ul_ele+='</ul>'
            ul_ele+=sub_ul_ele #和最外层的URL
        else:
            sub_ul_ele=''
        ul_ele+=sub_ul_ele
        for related_obj in obj._meta.related_objects:
            if 'ManyToManyRel'in related_obj.__repr__():
                if hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    # 上面accessor_obj 相当于 customer.enrollment_set
                    if hasattr(accessor_obj, 'select_related'):  # select——related==all
                        target_objs = accessor_obj.select_related()
                        sub_ul_ele="<ul style='color:red'>"
                        for o in target_objs:
                            li_ele = '''<li>%s:%s</li>''' % (o._meta.verbose_name, o.__str__().strip('<>'))
                            sub_ul_ele+=li_ele
                        sub_ul_ele+='</ul>'
                        ul_ele+=sub_ul_ele


            elif hasattr(obj,related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                accessor_obj=getattr(obj,related_obj.get_accessor_name())
                # 上面accessor_obj 相当于 customer.enrollment_set
                if hasattr(accessor_obj,'select_related'): #select——related==all
                    target_objs=accessor_obj.select_related()
                    # target_objs 相当于 customer.enrollment_set.all()
                else:#那就是onetoone
                    target_objs=accessor_obj
                if len(target_objs)>0:
                    nodes=recursive_related_objs_lookup(target_objs)
                    ul_ele+=nodes
    ul_ele+='</ul>'
    return ul_ele

@register.simple_tag
def get_action_verbose_name(admin_class,action):
    action_func=getattr(admin_class,action)
    return action_func.display_name if hasattr(action_func,'display_name') else action




