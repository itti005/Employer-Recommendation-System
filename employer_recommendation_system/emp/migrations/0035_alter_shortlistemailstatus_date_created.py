# Generated by Django 3.2 on 2021-07-23 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emp', '0034_auto_20210723_0514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortlistemailstatus',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
