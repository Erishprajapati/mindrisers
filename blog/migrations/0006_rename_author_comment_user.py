# Generated by Django 5.1.6 on 2025-02-15 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_post_image_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='author',
            new_name='user',
        ),
    ]
