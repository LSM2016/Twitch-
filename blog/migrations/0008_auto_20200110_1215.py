# Generated by Django 3.0.1 on 2020-01-10 04:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20200108_1515'),
    ]

    operations = [
        migrations.CreateModel(
            name='AsyncTask',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Edit',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('start_time', models.FloatField(default=0)),
                ('duration', models.FloatField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='clip',
            name='edit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.Edit'),
        ),
    ]
