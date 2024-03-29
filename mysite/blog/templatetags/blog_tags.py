from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
from django.urls import reverse

register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published_objects.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published_objects.order_by('-published')[:count]
    #print(latest_posts)
    return {'latest_posts':latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published_objects.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

@register.inclusion_tag('blog/post/nav_buttons.html')
def get_nav_buttons():
    return {
        'home_link': reverse('blog:post_list'),
        'home_title': 'Home'
    }