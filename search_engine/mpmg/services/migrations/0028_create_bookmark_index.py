# Generated by Django 3.0.5 on 2021-12-08 17:39

from django.db import migrations
from mpmg.services.elastic import Elastic
from elasticsearch_dsl import Keyword

def create_index(apps, schema_editor):
    elastic = Elastic()
    m = elastic.dsl.Mapping()
    m.field('id_pasta', 'text', fields={'keyword': Keyword()})
    m.field('id_usuario', 'text', fields={'keyword': Keyword()})
    m.field('indice_documento', 'text', fields={'keyword': Keyword()})
    m.field('id_documento', 'text')
    m.field('id_consulta', 'text')
    m.field('nome', 'text')
    m.field('id_sessao', 'text')
    m.field('data_criacao', 'date')
    m.field('data_modificacao', 'date')
    m.save('bookmark')

class Migration(migrations.Migration):
    dependencies = [
        ('services', '0027_create_config_recommendation_evidences_index'),
    ]

    operations = [
        migrations.RunPython(create_index)
    ]