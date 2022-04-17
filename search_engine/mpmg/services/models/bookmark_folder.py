from django.conf import settings

from datetime import datetime
from typing import Dict, List, Tuple

from elasticsearch.exceptions import NotFoundError
from mpmg.services.models.elastic_model import ElasticModel


class BookmarkFolder(ElasticModel):

    index_name = 'bookmark_folder'

    def __init__(self, **kwargs):
        index_name = BookmarkFolder.index_name
        meta_fields = ['id']
        index_fields = [
            'id_usuario',
            'id_pasta_pai',
            'nome',
            'data_criacao',
            'data_modificacao',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def _get_subfolders(self, id = str) -> list:
        elastic_result = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name) \
        .filter({'term': {'id_pasta_pai.keyword': id}}) \
        .execute() \
        .to_dict()
        
        elastic_result = elastic_result['hits']['hits']
        
        subfolders = list()
        for result in elastic_result:
            subfolders.append(result['_id'])
        
        return subfolders

    def _get_bookmarks(self, id = str) -> list:
        elastic_result = self.elastic.dsl.Search(using=self.elastic.es, index=settings.BOOKMARK_INDEX) \
        .filter({'term': {'id_pasta.keyword': id}}) \
        .execute() \
        .to_dict()

        elastic_result = elastic_result['hits']['hits']
         
        bookmarks = list()
        for result in elastic_result:
            bookmarks.append(result['_id'])
        
        return bookmarks

    def get(self, id: str) -> dict:
        try:
            retrieved_element = self.elastic.es.get(index=self.index_name, id=id)
        
        except NotFoundError:
            return None 

        source = retrieved_element['_source']
        element = {'id': retrieved_element['_id'], **source}

        element['subpastas'] = self._get_subfolders(id)
        element['favoritos'] = self._get_bookmarks(id)

        return element

    # Cria a pasta raiz do usuário, se ela não tiver sido criada
    def create_default_bookmark_folder_if_necessary(self, user_id) -> None:
        try:
            self.elastic.es.get(index=self.index_name, id=user_id)

        except NotFoundError:
            data = dict(
                criador=str(user_id),
                nome=settings.DEFAULT_BOOKMARK_FOLDER_NAME,
                pasta_pai=None,
            )

            super().save(data, user_id)

    def remove(self, folder_id):
        # TODO: Fazer essas operações serem atômicas

        folder = self.get(folder_id)
            
        for subfolder_id in folder['subpastas']:
            self.remove(subfolder_id)
        
        for bookmark_id in folder['favoritos']:
            self.elastic.es.delete(index=settings.BOOKMARK_INDEX, id=bookmark_id)

        self.elastic.es.delete(index=self.index_name, id=folder_id)

    def get_folder_tree(self, root_id: str) -> dict:
        folder = self.get(root_id)

        subpastas = []
        for subfolder_id in folder['subpastas']:
            subpastas.append(self.get_folder_tree(subfolder_id))

        folder['subpastas'] = subpastas
        return folder