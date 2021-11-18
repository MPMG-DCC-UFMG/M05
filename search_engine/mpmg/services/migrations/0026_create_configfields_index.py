# Generated by Django 3.0.5 on 2021-11-18 13:48

from django.db import migrations
from mpmg.services.elastic import Elastic

def create_index(apps, schema_editor):
    elastic = Elastic()
    m = elastic.dsl.Mapping()
    m.field('ui_name', 'text')
    m.field('field_name', 'text')
    m.field('weight', 'integer')
    m.field('searchable', 'boolean')
    m.field('retrievable', 'boolean')
    m.save('config_fields')


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0025_insert_configindices_data'),
    ]

    operations = [
        migrations.RunPython(create_index)
    ]
