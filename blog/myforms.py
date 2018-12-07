from django import forms
from django.forms import widgets
from blog import models
from django.core.exceptions import ValidationError

class MyForms(forms.Form):
    username=forms.CharField(max_length=6,min_length=2,label='用户名',widget=widgets.TextInput(attrs={'class':'layui-input'}),error_messages={'max_length':'长度不能超过6位','min_length':'长度不能少于2位','required': '不能为空'})
    password=forms.CharField(max_length=11,min_length=3,label='密码',widget=widgets.PasswordInput(attrs={'class':'layui-input'}),error_messages={'max_length':'长度不能超过11位','min_length':'长度不能少于3位','required': '不能为空'})
    raw_password=forms.CharField(max_length=11,min_length=3,label='确认密码',widget=widgets.PasswordInput(attrs={'class':'layui-input'}),error_messages={'max_length':'长度不能超过11位','min_length':'长度不能少于3位','required': '不能为空'})
    email=forms.EmailField(label='邮箱',widget=widgets.EmailInput(attrs={'class':'layui-input'}),error_messages={'required': '不能为空'})

    def clean_username(self):
        name=self.cleaned_data.get('username')
        ret=models.UserInfo.objects.filter(username=name).first()
        if ret:
            raise ValidationError('用户已存在')
        return name

    def clean(self):
        pwd=self.cleaned_data.get('password')
        re_pwd=self.cleaned_data.get('raw_password')
        if pwd==re_pwd:
            return self.cleaned_data
        else:
            raise ValidationError('两次密码不一致')
