#_author: hasee
#date: 2019/8/17
from django.forms import forms,ModelForm
from crm import  models
from django.forms import ValidationError
from django.utils.translation import ugettext as _

class CustomerModelForm(ModelForm):
    class Meta:
        model=models.Customer
        fields='__all__'

def create_model_form(request,admin_class):
        # 动态生成model form
    def __new__(cls,*args,**kwargs):
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class']='form-control'
            # field_obj.widget.attrs['maxlength'] =getattr(field_obj,'max_lenght') if hasattr(field_obj,'max_lenght') else ''
            if not hasattr(admin_class,'is_add_form'):#表示这是添加form，不需要disabled
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled']='disabled'
            if hasattr(admin_class,'clean_%s'%field_name):
                field_name_func=getattr(admin_class,'clean_%s'%field_name)
                print('1',field_name)
                print('2',field_name_func)
                setattr(cls,'clean_%s'%field_name,field_name_func)
        return ModelForm.__new__(cls)

    def default_clean(self):
        # 给所有的form默认加一个clean验证，虽然直接不能修改，但是可以吧代码打开修改里面的值，这样就可以通过判断前后2个值的区别来判断
        # print(self, admin_class)
        error_list=[]
        if self.instance.id:#有说明了是change
            for field in admin_class.readonly_fields:
                field_val = getattr(self.instance, field)#val in db
                if hasattr(field_val,'select_related'): #m2m
                    m2m_objs=getattr(field_val,'select_related')().select_related()
                    m2m_vals=[i[0] for i in m2m_objs.values_list('id')]
                    set_m2m_vals=set(m2m_vals)
                    set_m2m_vals_from_frontend=set[(i.id for i in self.cleaned_data.get(field))]
                    if set_m2m_vals!=set_m2m_vals_from_frontend:
                        # error_list.append(ValidationError(
                        #     _('Field %(field)s is readonly'),
                        #     code='invalid',
                        #     params={'field': 'field'},
                        # ))
                        self.add_error(field,'readonly field')
                        continue
                field_val_from_frontend = self.cleaned_data.get(field)
                if field_val!=field_val_from_frontend:
                    error_list.append(ValidationError(
                        _('Field %(field)s is readonly,data should be $(val)s'),
                        code='invalid',
                        params={'field': 'field','val':field_val},
                    ))
        #readonly_table check
        if admin_class.readonly_table:
            raise ValidationError(
                        _('Table is readonly,cannot be modified or added'),
                        code='invalid',
                    )
            #invoke user's customized form validation
        self.ValidationError=ValidationError
        response=admin_class.default_form_validation(self)
        if response:
            error_list.append(response)
        if error_list:
            # print(error_list)
            raise ValidationError(error_list)
    class Meta:
        model=admin_class.model
        fields='__all__'
        exclude=admin_class.modelform_exclude_fields
    attrs={'Meta':Meta,}
    _model_form_class=type('DynamicModelForm',(ModelForm,),attrs)
    setattr(_model_form_class,'__new__',__new__)
    setattr(_model_form_class, 'clean', default_clean)
    # setattr(_model_form_class,'Meta',Meta)
    return _model_form_class