

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20200425_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('none', 'None'), ('employer', 'Employer'), ('employee', 'Employee')], max_length=10),
        ),
    ]
