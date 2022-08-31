from turtle import update
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager
from decimal import Decimal

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='published')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', help_text='Search and select an author')
    body = models.TextField()
    published = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=Decimal('0.0'))
    duration = models.DecimalField(max_digits=2, decimal_places=1, default=Decimal('0.0'))

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                        args=[self.published.day,
                              self.published.month,
                              self.published.year,
                              self.slug
                        ]        
        )
    
    objects = models.Manager()
    published_objects = PublishedManager()
    tags = TaggableManager()

    class Meta:
        ordering = ('-published',)

    def __str__(self):
        return self.title

class Comment(models.Model):
    # Many to one
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # remove inappropriate comments
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'comment by {} on {}'.format(self.name, self.post) 