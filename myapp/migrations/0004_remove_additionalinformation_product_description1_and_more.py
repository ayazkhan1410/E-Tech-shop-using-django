# Generated by Django 5.0 on 2024-03-03 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_remove_additionalinformation_product_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='additionalinformation',
            name='product_description1',
        ),
        migrations.RemoveField(
            model_name='additionalinformation',
            name='product_description2',
        ),
        migrations.AddField(
            model_name='additionalinformation',
            name='exisiting_product_description1',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='additionalinformation',
            name='new_product_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='additionalinformation',
            name='new_product_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]