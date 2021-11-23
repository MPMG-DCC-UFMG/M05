import hashlib
from elasticsearch.transport import get_host_info
from elasticsearch_dsl.aggs import Pipeline

from rest_framework.response import Response

from mpmg.services.elastic import Elastic
from mpmg.services.models import ElasticModel
from mpmg.services.models import bookmark_folder
from mpmg.services.models.bookmark_folder import BookmarkFolder

class Bookmark(ElasticModel):
    index_name = 'bookmark'

    def __init__(self, **kwargs):
        index_name = Bookmark.index_name
        meta_fields = ['id']
        index_fields = [
            'id_folder',
            'nome',
            'index',
            'item_id',
            'id_sessao',
            'consulta',
            'data_criacao'
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def get_id(self, index: str, item_id: str) -> str:
        return hashlib.sha1((index + item_id).encode()).hexdigest()

    def save(self, dict_data=None):
        if dict_data == None:
            dict_data = {}
            for field in self.index_fields:
                dict_data[field] = getattr(self, field, '')

        if BookmarkFolder().get_item(dict_data['id_folder']) is None:
            return None 

        bookmark_id = self.get_id(dict_data['index'], dict_data['item_id'])

        es = Elastic().es
        result = es.index(index=self.index_name, id=bookmark_id, body=dict_data)
        
        BookmarkFolder().add_file(dict_data['id_folder'], result['_id'])

        return bookmark_id


    def get_item(self, id_bookmark):
        try:
            data = Elastic().es.get(index=self.index_name, id=id_bookmark)['_source']        
            data['id'] = id_bookmark
            return data
            
        except:
            return None

    def get_item_by_index_and_item_id(self, index, item_id):
        bookmark_id = self.get_id(index, item_id)
        return self.get_item(bookmark_id)

    def remove(self, id_bookmark):
        try:
            bookmark = self.get_item(id_bookmark)

            id_folder = bookmark['id_folder']
            result = BookmarkFolder().remove_file(id_folder, id_bookmark)
            
            if not result:
                return result

            response = Elastic().es.delete(index=self.index_name, id=id_bookmark)

            return response['result'] == 'deleted'

        except:
            return False 

    def change_folder(self, id_bookmark, id_new_folder):
        bookmark = self.get_item(id_bookmark)
        id_folder = bookmark['id_folder']

        bookmark_folder = BookmarkFolder()
        bookmark_folder.remove_file(id_folder, id_bookmark)
        
        bookmark_folder.add_file(id_new_folder, id_bookmark)

        response = Elastic().es.update(index=self.index_name, id=id_bookmark, body={"doc": {"id_folder": id_new_folder}})
        return response['result'] == 'updated'