#_author: hasee
#date: 2019/9/8
from django.utils.safestring import mark_safe
from django import template
from django.utils.timezone import datetime,timedelta
from django.core.exceptions import FieldDoesNotExist
register=template.Library()

@register.simple_tag
def render_enroll_contract(enroll_obj):
    print('33',enroll_obj.enrolled_class)
    return enroll_obj.enrolled_class.contract.template.\
        format(course_name=enroll_obj.enrolled_class,stu_name=enroll_obj.customer.qq)

