from django.template import Library
from blog import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register=Library()

@register.inclusion_tag('classify.html')
def classify(username):
    user=models.UserInfo.objects.filter(username=username).first()
    blog=user.blog
    category_num=models.Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title','c','pk')
    tag_num=models.Tag.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title','c','pk')
    y_m_num=models.Article.objects.filter(blog=blog).annotate(y_m=TruncMonth('create_time')).values('y_m').annotate(c=Count('y_m')).values_list('y_m','c')
    # print(category_num,tag_num,y_m_num)
    return {'category_num':category_num,'tag_num':tag_num,'y_m_num':y_m_num,'username':username}