# Generated by Django 4.2.5 on 2023-09-22 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_pic', django_resized.forms.ResizedImageField(blank=True, crop=None, default='def.jpg', force_format=None, keep_meta=True, null=True, quality=100, scale=None, size=[50, 80], upload_to='profile_pictures/')),
                ('bio', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=400, unique=True)),
                ('hidden', models.BooleanField(default=False)),
                ('hidden_profile', models.BooleanField(default=False)),
                ('user', models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
