# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20251027_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='display_value',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
