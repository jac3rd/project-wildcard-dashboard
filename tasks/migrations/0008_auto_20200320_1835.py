# Generated by Django 3.0.2 on 2020-03-20 22:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='user_id',
            new_name='user',
        ),
    ]
