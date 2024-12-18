# Generated by Django 5.1.1 on 2024-10-04 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplements', '0008_creatine_form_alter_creatine_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='creatine',
            name='capsule_amount',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='creatine',
            name='capsule_weight',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='creatine',
            name='type',
            field=models.CharField(choices=[('monohydrate', 'Monohidratada'), ('creapure', 'Creapure®'), ('micronised', 'Micronizada')], max_length=20),
        ),
        migrations.AlterField(
            model_name='proteinpowder',
            name='type',
            field=models.CharField(choices=[('concentrate', 'Concentrado'), ('isolate', 'Isolado'), ('clear', 'Clear'), ('blend', 'Blend')], max_length=20),
        ),
    ]
