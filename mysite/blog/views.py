from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Comment
from taggit.models import Tag
from .forms import EmailPostForm, CommentForm, SearchForm
from django.http import HttpRequest
from django.core.mail import send_mail
from django.db.models import Count
from django.conf import settings
import smtplib
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

def post_list(request, tag_slug=None):
    object_list = Post.published_objects.all()
    tag = None
    if tag_slug:
        # get the tag object
        tag = get_object_or_404(Tag, slug=tag_slug)
        # get all posts with given tag
        object_list = object_list.filter(tags__in=[tag])
    # 3 posts per page
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page':page, 'posts': posts, 'tag':tag})

def post_detail(request, day, month, year, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   published__year=year,
                                   published__month=month,
                                   published__day=day)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published_objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-published')[:2]

    # get all the comments for post
    comments = post.comments.filter(active=True)
    
    new_comment = None  
    if request.method == 'POST':
        # create a form instance and bound data
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # save creates an model instance
            # create instance but dont commit to db
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            # commit new comment object to db
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post':post, 'comments':comments, 'new_comment':new_comment, 'comment_form':comment_form, 'similar_posts':similar_posts})

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    error = None

    # if form is submitted
    if request.method == 'POST':
        # bound the form with data
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # build complete uri(along with domain) from absolute url
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = "{} ({}) recommends you reading {}".format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            # try to send email
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['to']], fail_silently=False)
            except smtplib.SMTPException as e:
                error = e
            else:   
                sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post':post, 
                                                    'form':form, 
                                                    'sent':sent,
                                                    'error':error})

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # create tsvector and tsquery
            search_query = SearchQuery(query)
            search_vector = SearchVector('title', 'body')
            # search title and body of post and order results by rank
            results = Post.published_objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank')
            results = results.filter(rank__gte=0.01)
    return render(request, 'blog/post/search.html', {'form':form,
                                'query': query,
                                'results':results})