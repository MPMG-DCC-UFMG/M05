# Generated by Django 3.0.5 on 2020-09-08 20:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_auto_20200827_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='max_result_window',
            field=models.PositiveIntegerField(default=10000, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='config',
            name='num_repl',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(50), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='config',
            name='algorithm',
            field=models.CharField(choices=[('BM25', 'Okapi BM25'), ('DFR', 'Divergence from Randomness (DFR)'), ('DFI', 'Divergence from Independence (DFI)'), ('IB', 'Information based model'), ('LMDirichlet', 'Language Model: Dirichlet priors'), ('LMJelinekMercer', 'Language Model: Jelinek-Mercer smoothing method')], default='BM25', max_length=50),
        ),
    ]