from django.shortcuts import render,HttpResponse,redirect
from PIL import Image,ImageDraw,ImageFont
from random import choice
import random
import string
from django.contrib.auth import login,logout,authenticate
from django.http import JsonResponse
from BBS import settings
from blog import models
import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.db.utils import IntegrityError
from io import BytesIO
from django.db.models import Count
import os

# import smtplib
# from email.mime.text import MIMEText
# from email.header import Header

from django.core.mail import send_mail
import threading



# Create your views here.

# 登录
def login_user(request):
    if request.method=='GET':
        return render(request,'login.html')
    elif request.method=='POST':
        response={'user':None,'msg':None}
        yzm=request.session['yzm']
        valid_code = request.POST.get('yzm')
        username=request.POST.get('username')
        password=request.POST.get('password')

        if yzm.upper()==valid_code.upper():
            user=authenticate(username=username,password=password)
            if user:
                login(request,user)
                response['user']=username
                response['msg']='登录成功'
            else:
                response['msg']='用户名或密码错误'
        else:
            response['msg']='验证码错误'
        return JsonResponse(response)

#随机验证码
def get_valid_code(request):
    # 方式一：写死
    # with open('static/img/yz.jpg','rb') as f:
    #     data=f.read()
    # return HttpResponse(data)

    #方式二：随机颜色
    # img=Image.new('RGB',(320,36),color=get_random_color())
    # with open('static/img/valid_code.png','wb') as f:
    #     img.save(f,'png')
    #
    # with open('static/img/valid_code.png','rb') as f:
    #     data=f.read()
    # return HttpResponse(data)

    #方式三：在内存中生成一个空文件
    # img=Image.new('RGB',(320,36),color=get_random_color())
    # f=BytesIO()
    # img.save(f,'png')
    # data=f.getvalue()
    # return HttpResponse(data)

    #方式四： 在图片上写文字
    img=Image.new('RGB',(320,36),get_random_color())
    img_draw=ImageDraw.Draw(img)#将图片传入画笔
    #生成字体对象
    font=ImageFont.truetype('static/font/ss.TTF',size=32)

    # 随机五个验证码
    random_code=''
    for i in range(1):
        A=random.choice(string.ascii_uppercase)
        a=random.choice(string.ascii_lowercase)
        n=random.choice(string.ascii_letters)
        r=random.choice([A,a,n])
        img_draw.text((i * 50 + 20, 0), r, get_random_color(), font=font)
        random_code += r
    request.session['yzm']=random_code

    width=320
    height=35
    # 画线
    # for i in range(5):
    #
    #     x1=random.randint(0,width)
    #     x2=random.randint(0,width)
    #     y1=random.randint(0,height)
    #     y2=random.randint(0,height)
    #     img_draw.line((x1,y1,x2,y2),fill=get_random_color())

    # 画点
    # for i in range(80):
    #
    #     img_draw.point([random.randint(0,width),random.randint(0,height)],fill=get_random_color())
    #     x=random.randint(0,width)
    #     y=random.randint(0,height)
    #     img_draw.arc((x,y,x+4,y+4),0,90,fill=get_random_color())

    f=BytesIO()
    img.save(f,'png')
    data=f.getvalue()
    return HttpResponse(data)

#随机颜色
def get_random_color():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))

# 注册
from .myforms import MyForms
def register(request):
    if request.method=='GET':
        myform=MyForms()
        return render(request,'register.html',locals())
    elif request.is_ajax():
        response={'status':100,'msg':None}
        myform=MyForms(request.POST)
        if myform.is_valid():
            arr =myform.cleaned_data
            arr.pop('raw_password')
            img_file=request.FILES.get('img_file')
            if img_file:
                arr['avatar']=img_file

            user=models.UserInfo.objects.create_user(**arr)
            blog=models.Blog.objects.create(title='默认title',site_name=user.username)
            user.blog=blog
            user.save()
            response['msg']='注册成功'
            print(user.username)
            return JsonResponse(response)
        else:
            response['status']=0
            response['msg']=myform.errors
            return JsonResponse(response)

#检测用户名是否重复
def check_username(request):
    response={'status':100,'msg':None}
    if request.is_ajax():
        name=request.POST.get('name')
        username=models.UserInfo.objects.filter(username=name).first()
        if username:
            response['status']=0
            response['msg']='用户名已被使用'
        return JsonResponse(response)

#修改个人信息
@login_required(login_url='/login/')
def up_userinfo(request):
    if request.method=='GET':
        form=MyForms()
        return render(request,'up_userinfo.html',locals())
    elif request.method=='POST':
        user=request.user
        myfile=request.FILES.get('myfile')
        pwd1=request.POST.get('password')
        pwd2=request.POST.get('raw_password')
        print(myfile.name)
        if pwd1==pwd2:
            user.avatar=myfile
            user.set_password(pwd1)
            user.save()
        return HttpResponse('1')

# 首页
def index(request):
    article_list=models.Article.objects.all()
    MEDIA_URL=settings.MEDIA_URL
    return render(request,'index.html',locals())

def logout_user(request):
    logout(request)
    return redirect('/index/')

def user_blog(request,username,*args,**kwargs):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse('请求页面不存在')
    blog=user.blog
    article_list=blog.article_set.all()

    condition = kwargs.get('condition')
    param=kwargs.get('param')
    # print(condition,param)
    # print(article_list)
    if condition=='tag':
        print(param)
        article_list=article_list.filter(articletotag__tag__pk=param)
        print(article_list)
    elif condition=='category':
        article_list = article_list.filter(category__pk=param)
        print(article_list)
    elif condition=='archive':
        archive_list = param.split('-')
        print(article_list)
        article_list = article_list.filter(create_time__year=archive_list[0],create_time__month=archive_list[1])
        print(article_list)

    return render(request,'user_blog.html',locals())

def article_detail(request,username,id):
    article=models.Article.objects.filter(pk=id).first()
    commint_list=models.Commit.objects.filter(article=article)
    return render(request,'article_detail.html',locals())

# 点赞
def diggit(request):
    if request.is_ajax():
        response={'status':100,'msg':None}
        article_id=request.POST.get('article_id')
        is_up=request.POST.get('is_up')
        is_up=json.loads(is_up)

        if request.user.is_authenticated():
            ret=models.UpAndDown.objects.filter(article_id=article_id,user=request.user).exists()
            if ret:
                response['status'] = 110
                response['msg'] = '您已经操作过了'
            else:
                with transaction.atomic():
                    models.UpAndDown.objects.create(user=request.user,article_id=article_id,is_up=is_up)
                    articel=models.Article.objects.filter(pk=article_id)
                    if is_up:
                        articel.update(up_num=F('up_num')+1)
                        response['msg']='点赞成功'
                    else:
                        articel.update(down_num=F('down_num') + 1)
                        response['msg'] = '点踩成功'
        else:
            response['status']=120
            response['msg']='请先登录'

    # if request.user.is_authenticated():
    #     try:
    #         with transaction.atomic():
    #             user=models.UpAndDown.objects.create(user=request.user,article_id=articel_id,is_up=is_up)
    #             up=models.Article.objects.filter(pk=articel_id).update(up_num=F('up_num')+1)
    #             response['msg'] = '点赞成功'
    #     except IntegrityError as e:response['msg']='请勿重复操作'
    # else:
    #     response['status']=101
    #     response['msg']='清先登录'

        return JsonResponse(response)


# 评论发送邮件
# msg_from='785484564@qq.com' #发送方邮箱
# passwd='wdcljdnqervebefe'  #发送方授权码


# 评论
def comment_submit(request):
    if request.is_ajax():
        response={'status':100,'msg':None}
        if request.user.is_authenticated():
            user=request.user
            article_id=request.POST.get('article_id')
            text=request.POST.get('text')
            pid=request.POST.get('pid')

            with transaction.atomic():
                ret=models.Commit.objects.create(user=user,article_id=article_id,content=text,parent_id=pid)
                models.Article.objects.filter(pk=article_id).update(commit_num=F('commit_num')+1)

            response['text']=ret.content
            response['time']=ret.commit_time.strftime('%Y-%m-%d %X')
            response['user']=ret.user.username
            if pid:
                response['parent_name']=ret.parent.user.username
            print(response)

            #收件人邮箱
            # msg_to=['zfeijun@foxmail.com']
            # subject='博客园更新'
            # content='''
            # <p>Python 邮件发送测试...</p>
            # <p><a href="http://www.baidu.com">这是一个链接</a></p>
            # '''
            # msg=MIMEText(content) #生成MIMEText对象
            # msg['Subject']=subject  #放入邮件主题
            # msg['From']=msg_from  #放入发件人
            # msg['To']='zfeijun@foxmail.com'
            #
            # s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            # s.login(msg_from, passwd)
            # # 发送邮件：发送方，收件方，要发送的消息
            # s.sendmail(msg_from, msg_to, msg.as_string())
            # print('成功')

            #Django模式下发送邮件
            t=threading.Thread(target=send_mail,args=('你的文章新增了一条评论内容','哈哈哈',settings.EMAIL_HOST_USER,['zfeijun@foxmail.com']))

            t.start()

            response['msg']='评论成功'
        else:
            response['status']=101
            response['msg']='请先登录'
        return JsonResponse(response)

@login_required(login_url='/login/')
def backed(request):
    if request.method=='GET':
        article_list=models.Article.objects.filter(blog=request.user.blog)
        print(article_list)
        return render(request, 'back/backend.html', locals())

from bs4 import BeautifulSoup
@login_required(login_url='/login/')
def add_article(request):
    if request.method == 'GET':
        return render(request, 'back/add_article.html', locals())
    elif request.method=='POST':
        title=request.POST.get('title')
        content=request.POST.get('content')

        soup=BeautifulSoup(content,'lxml')
        # 找出所有的标签
        tags=soup.find_all()
        for tag in tags:
            if tag.name=='script':
                # 删除有script的标签
                tag.decompose()

        # print(soup)
        desc=soup.text[0:150]
        models.Article.objects.create(title=title,content=content,desc=desc,blog=request.user.blog)
    return redirect('/backed/')


def upload_img(request):
    myfile=request.FILES.get('myfile')
    name=request.user.username
    path=os.path.join(settings.BASE_DIR,'media','img',name)

    if not os.path.exists(path):
        os.makedirs(path)
    file_path=os.path.join(path,myfile.name)
    with open(file_path,'wb') as f:
        for i in myfile:
            f.write(i)
    dic={
        "error": 0,
        "url": "/media/img/zfj/%s" %myfile.name
    }
    return JsonResponse(dic)

def up_article(request,id):
    if request.method=='GET':
        article_pk=id
        return render(request,'back/up_article.html',locals())

def get_article(request,id):
    article=models.Article.objects.filter(pk=id).first()
    return JsonResponse({'title':article.title,'content':article.content})