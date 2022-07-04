# Generated by Django 4.0 on 2022-06-30 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('blog', '0004_post_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(help_text='Search and select an author', on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to='auth.user'),
        ),
    ]