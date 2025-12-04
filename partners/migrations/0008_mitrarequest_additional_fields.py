# Generated migration for adding additional fields to MitraRequest

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0007_alter_laundry_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='mitrarequest',
            name='address',
            field=models.TextField(default='', verbose_name='Alamat'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mitrarequest',
            name='phone_number',
            field=models.CharField(max_length=20, default='', verbose_name='Nomor Telepon'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mitrarequest',
            name='bank_name',
            field=models.CharField(max_length=100, blank=True, verbose_name='Nama Bank'),
        ),
        migrations.AddField(
            model_name='mitrarequest',
            name='account_number',
            field=models.CharField(max_length=50, blank=True, verbose_name='Nomor Rekening'),
        ),
        migrations.AddField(
            model_name='mitrarequest',
            name='account_holder',
            field=models.CharField(max_length=200, blank=True, verbose_name='Atas Nama'),
        ),
    ]
