# Generated by Django 3.0.7 on 2020-06-26 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_reviewinvitation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='claim',
            options={'ordering': ['-id']},
        ),
        migrations.RemoveField(
            model_name='claim',
            name='topic',
        ),
        migrations.AddField(
            model_name='claim',
            name='topics',
            field=models.ManyToManyField(blank=True, related_name='claims', to='api.Topic'),
        ),
    ]
