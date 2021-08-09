# Generated by Django 2.2.18 on 2021-08-09 07:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Web',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=100)),
                ('shortname', models.CharField(max_length=100)),
                ('last_fuzzer', models.CharField(default='', max_length=100)),
                ('fuzzer_status', models.CharField(default='', max_length=100)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Fuzzer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('threads', models.IntegerField()),
                ('wordlist', models.CharField(max_length=100)),
                ('user_agent', models.CharField(max_length=100)),
                ('extensions', models.CharField(max_length=100)),
                ('hide_codes', models.CharField(max_length=100)),
                ('verb', models.CharField(max_length=10)),
                ('proxy', models.CharField(default='', max_length=100)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Finding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=100)),
                ('url', models.CharField(default='', max_length=100)),
                ('size', models.CharField(default='0', max_length=100)),
                ('code', models.CharField(default='-', max_length=100)),
                ('web', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Web')),
            ],
        ),
    ]
