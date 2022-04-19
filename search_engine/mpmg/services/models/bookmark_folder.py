from django.conf import settings

from elasticsearch.exceptions import NotFoundError
from mpmg.services.models.elastic_model import ElasticModel
from mpmg.services.utils import doc_filter 

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

    def _get_subfolders(self, folder_id = str) -> list:
        ''' Retorna as subpastas da pasta folder_id.

        Args:
            - folder_id: ID da pasta a ter subpastas recuperadas.

        Returns:
            Retorna uma lista onde cada elemento é um dicionário representando as subpastas da pasta folder_id.

        '''
        
        subfolders_found = doc_filter(self.index_name, {'term': {'id_pasta_pai.keyword': folder_id}})
        
        subfolders_ids = list()
        for subfolder_found in subfolders_found:
            source = subfolder_found['_source']
            subfolders_ids.append({'id': subfolder_found['_id'], **source})
        
        return subfolders_ids

    def _get_bookmarks(self, folder_id = str) -> list:
        ''' Retorna a lista de bookmarks salvos na pasta folder_id.

        Args:
            - folder_id: ID da pasta a ser obtido os bookmarks.

        Returns:
            Retorna uma lista onde cada elemento é um dicionário com a representação de um bookmark salvo na pasta folder_id.

        '''
        
        bookmarks_found = doc_filter(settings.BOOKMARK_INDEX, {'term': {'id_pasta.keyword': folder_id}}) 
         
        bookmarks_ids = list()
        for bookmark_found in bookmarks_found:
            source = bookmark_found['_source']
            bookmarks_ids.append({'id': bookmark_found['_id'], **source})
        
        return bookmarks_ids

    def get(self, folder_id: str) -> dict:
        '''Recupera a pasta de ID folder_id.

        Args:
            - folder_id: ID da pasta a ser recuperada.

        Returns:
            Retorna um dicionário com a representação da pasta folder_id.

        '''
        
        try:
            retrieved_element = self.elastic.es.get(index=self.index_name, id=folder_id)
        
        except NotFoundError:
            return None 

        source = retrieved_element['_source']
        element = {'id': retrieved_element['_id'], **source}

        element['subpastas'] = self._get_subfolders(folder_id)
        element['favoritos'] = self._get_bookmarks(folder_id)

        return element

    def create_default_bookmark_folder_if_necessary(self, user_id: str):
        ''' Cria uma pasta default para um usuário caso ela não tenha uma.

        Args:
            - user_id: ID do usuário a ter uma pasta default criada.
        '''
        
        try:
            self.elastic.es.get(index=self.index_name, id=user_id)

        except NotFoundError:
            data = dict(
                criador=str(user_id),
                nome=settings.DEFAULT_BOOKMARK_FOLDER_NAME,
                pasta_pai=None,
            )

            super().save(data, user_id)

    def delete(self, folder_id: str) -> bool:
        ''' Deleta a pasta folder_id junto com todas suas subpastas e bookmarks.

        TODO: Tornar as operações feitas aqui atômicas.

        Args:
            - folder_id: ID da pasta a ser deletada.

        Returns:
            Retorna True se a última deleção ocorreu corretamente, False, caso contrário.
        '''
        folder = self.get(folder_id)
            
        for subfolder in folder['subpastas']:
            self.delete(subfolder['id'])
        
        for bookmark in folder['favoritos']:
            self.elastic.es.delete(index=settings.BOOKMARK_INDEX, id=bookmark['id'])

        response = self.elastic.es.delete(index=self.index_name, id=folder_id)
        return response['result'] == 'deleted'

    def get_folder_tree(self, folder_id: str) -> dict:
        '''Retorna a árvore de pastas a partir de folder_id. 

        Args:
            - folder_id: ID da pasta base para criar a árvore de pastas.
        
        Returns:
            Retorna um dicionário representando a árvore de pastas.
            
        '''
        
        folder = self.get(folder_id)

        subpastas = list()
        for subfolder in folder['subpastas']:
            subfolder_id = subfolder['id']
            subpastas.append(self.get_folder_tree(subfolder_id))

        folder['subpastas'] = subpastas
        return folder