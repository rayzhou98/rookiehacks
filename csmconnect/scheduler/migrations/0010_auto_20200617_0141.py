# Generated by Django 3.0.6 on 2020-06-17 01:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0009_remove_siteuser_short_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='siteuser',
            old_name='description',
            new_name='short_description',
        ),
    ]
