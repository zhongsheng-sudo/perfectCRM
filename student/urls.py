from django.urls import path,re_path
from student import views


urlpatterns = [
    path('', views.stu_my_classes,name='stu_my_classes'),
    re_path(r'^studyrecords/(\d+)/$', views.studyrecords,name='studyrecords'),
    re_path(r'^homework_detail/(\d+)/$', views.homework_detail,name='homework_detail'),
]
