# Generated by Django 2.2.5 on 2019-10-20 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0006_auto_20191015_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='stu_account',
            field=models.ForeignKey(blank=True, help_text='只有学员报名后方可为其创建账号', null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.Customer', verbose_name='关联学员账号'),
        ),
        migrations.AlterField(
            model_name='courserecord',
            name='day_num',
            field=models.PositiveIntegerField(verbose_name='第几节课(天)'),
        ),
    ]
