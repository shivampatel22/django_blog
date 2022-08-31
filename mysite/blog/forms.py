from django import forms
from .models import Comment, Post

def get_rating_choices():
    rating_choices = [
        ('0', 'All'),
        ('5', '5 and above'),
        ('7', '7 and above'),
        ('8', '8 and above'),
    ]
    return rating_choices

def get_duration_choices():
    duration_choices = [
        ('0', 'All'),
        ('1', 'short'),
        ('2', 'medium'),
        ('3', 'long'),
    ]
    return duration_choices

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    # create form from model directly 
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

class SearchForm(forms.Form):
    # Form for full text search
    query = forms.CharField()

class FilterForm(forms.Form):
    # get choices
    rating_choices = get_rating_choices()
    duration_choices = get_duration_choices()
    # Form for filter pannel
    tags_filter = forms.ModelMultipleChoiceField(label='By Tags', queryset=Post.tags.all())
    rating_filter = forms.ChoiceField(label='By Rating', choices=rating_choices)
    duration_filter = forms.ChoiceField(label='By Duration', choices=duration_choices)
    title_filter = forms.CharField(max_length=25, label='By Title', required=False)
