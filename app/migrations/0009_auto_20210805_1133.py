# Generated by Django 2.2.18 on 2021-08-05 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_fuzzer_proxy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='web',
            name='fuzzers',
        ),
        migrations.AddField(
            model_name='web',
            name='last_fuzzer',
            field=models.CharField(default='', max_length=100),
        ),
    ]