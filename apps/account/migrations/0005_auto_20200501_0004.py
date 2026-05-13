

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20200501_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('none', 'None'), ('employer', 'Employer'), ('employee', 'Employee')], max_length=10),
        ),
    ]
