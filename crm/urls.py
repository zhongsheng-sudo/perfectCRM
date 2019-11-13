from django.urls import path,re_path
from  crm import views


urlpatterns = [
    path('', views.index,name='sales_index'),
    re_path(r'^customer/(\d+)/enrollment/$', views.enrollment,name='enrollment'),
    re_path(r'^customer/registration/(\d+)/(\w+)/', views.stu_registration,name='stu_registration'),
    re_path(r'^contract_review/(\d+)/', views.contract_review,name='contract_review'),
    re_path(r'^payment/(\d+)/', views.payment,name='payment'),
    re_path(r'^enrollment_rejection/(\d+)/', views.enrollment_rejection,name='enrollment_rejection'),
    path('customers/', views.customer_list,name='customer_list'),
]
