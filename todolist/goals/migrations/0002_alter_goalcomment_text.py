# Generated by Django 4.2 on 2023-05-03 16:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goalcomment',
            name='text',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]