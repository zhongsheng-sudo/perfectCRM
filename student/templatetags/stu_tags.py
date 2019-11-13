#_author: hasee
#date: 2019/9/14
from django.utils.safestring import mark_safe
from django import template
from django.utils.timezone import datetime,timedelta
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Sum
register=template.Library()

@register.simple_tag
def get_score(enroll_obj,customer_obj):
    study_records=enroll_obj.studyrecord_set.filter(course_record__from_class_id=enroll_obj.enrolled_class.id)
    print(enroll_obj)
    print(enroll_obj.enrolled_class.id)
    for record in study_records:
        print(record)
    return study_records.aggregate(Sum('score'))