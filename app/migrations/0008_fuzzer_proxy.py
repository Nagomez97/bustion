# Generated by Django 2.2.18 on 2021-08-05 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_finding_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuzzer',
            name='proxy',
            field=models.CharField(default='', max_length=100),
        ),
    ]