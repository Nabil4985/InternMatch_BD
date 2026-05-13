

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0007_alter_job_experience_level_alter_job_work_mode'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Category',
            new_name='Skill',
        ),
        migrations.RemoveField(
            model_name='job',
            name='category',
        ),
        migrations.AddField(
            model_name='job',
            name='skills',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='jobapp.skill'),
        ),
    ]
