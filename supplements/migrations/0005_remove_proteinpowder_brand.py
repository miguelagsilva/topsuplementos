# Generated by Django 5.1.1 on 2024-09-26 23:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supplements', '0004_proteinpowder_from_brand'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proteinpowder',
            name='brand',
        ),
    ]