# Generated by Django 5.1.1 on 2024-09-26 22:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplements', '0002_alter_proteinpowder_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('website_url', models.URLField()),
            ],
        ),
    ]
