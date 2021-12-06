import hashlib
from typing import Union
from elasticsearch.transport import get_host_info
from elasticsearch_dsl.aggs import Pipeline
from rest_framework import response

from rest_framework.response import Response

from mpmg.services.elastic import Elastic
from mpmg.services.models import ElasticModel
from mpmg.services.models import bookmark_folder
from mpmg.services.models.bookmark_folder import BookmarkFolder

class Bookmark(ElasticModel):
    index_name = 'bookmark'
    es = Elastic().es
    bookmark_folder = BookmarkFolder() 

    def __init__(self, **kwargs):
        index_name = Bookmark.index_name
        meta_fields = ['id']
        index_fields = [
            'id_pasta',
            'id_sessao',
            'indice_documento',
            'id_documento',
            'nome',
            'consulta',
            'data_criacao'
            'data_modificacao'
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def get_id(self, indice_documento: str, id_documento: str) -> str:
        '''Retorna o ID de um bookmark, baseado em qual índice ele está e ID do documento que ele registra.

        Args:
            - indice_documento: Índice do documento a ser salvo pelo bookmark.
            - id_documento: ID do documento a ser salvo pelo bookmark.

        Returns:
            Retorna o ID de um bookmark, baseado na hash SHA-1 do índice e ID do documento que ele salva.

        '''
        
        return hashlib.sha1((indice_documento + id_documento).encode()).hexdigest()

    def save(self, dict_data: dict = None) -> Union[str, None]:
        ''' Salva o bookmark no índice. 
        
        Chaves passadas em dict_data que não estiverem especificadas em index_fields serão ignoradas. 
        Se dict_data for igual a None, os atributos do objeto é que serão salvos.
        
        Args:
            - dict_data: Representa os valores a serem salvos. Chaves passadas em dict_data que não 
                        estiverem especificadas em index_fields serão ignoradas. Se dict_data 
                        for igual a None, os atributos do objeto é que serão salvos.

        Returns:
            Retorna um string retorna o ID do bookmark criado ou None, se não foi possível criá-lo.

        '''        
        
        if dict_data == None:
            dict_data = {}
            for field in self.index_fields:
                dict_data[field] = getattr(self, field, '')

        if BookmarkFolder().get(dict_data['id_pasta']) is None:
            return None 

        bookmark_id = self.get_id(dict_data['indice_documento'], dict_data['id_documento'])

        result = self.es.index(index=self.index_name, id=bookmark_id, body=dict_data)
        
        BookmarkFolder().add_file(dict_data['id_pasta'], result['_id'])

        return bookmark_id


    def get(self, id_bookmark: str) -> Union[dict, None]:
        ''' Recupa um bookmar por seu ID id_bookmark.

        Args:
            - id_bookmark: ID do bookmark a ser recuperado.

        Returns:
            Retorna um dicionário representando o bookmark, ou None, se não foi possível recuperá-lo.
        '''
        
        try:
            data = self.es.get(index=self.index_name, id=id_bookmark)['_source']        
            data['id'] = id_bookmark
            return data
            
        except:
            return None

    def get_by_index_and_id_documento(self, indice_documento: str, id_documento: str) -> Union[dict, None]:
        '''Recupa um bookmark pelo indice e identificado do documento que ele registra.

        Args:
            - indice_documento: Indice do documento que o bookmark está salvando.
            - id_documento: ID do documento sendo salvo pelo bookmark no índice `indice_documento`.

        Returns:
            Retorna a representação do bookmark em dicionário, ou None, caso contrário.
        
        '''

        bookmark_id = self.get_id(indice_documento, id_documento)
        return self.get(bookmark_id)

    def remove(self, id_bookmark: str) -> Union[bool, str]:
        ''' Remove o bookmark de ID id_bookmark.

        Args:
            - id_bookmark: ID do bookmark a ser removido.

        Returns:
            Returna uma tupla onde a primeira posição é `False`, se houve alguma erro ao 
            remover o bookmark. `True` caso contrário. A segunda posição é uma string que 
            informa o erro, se o houver.
        
        '''

        bookmark = self.get(id_bookmark)

        if bookmark is None:
            return False, 'Não foi possível encontrar o bookmark!'

        id_pasta = bookmark['id_pasta']
        success = BookmarkFolder().remove_file(id_pasta, id_bookmark)
        
        if not success:
            return False, 'Não foi possível remover o bookmark de sua pasta!'

        response = self.es.delete(index=self.index_name, id=id_bookmark)
        success = response['result'] == 'deleted'

        msg_error = ''
        if not success:
            msg_error = 'Não foi possível remover o bookmark!'
            BookmarkFolder().add_file(id_pasta, id_bookmark)

        return success, msg_error

    def update(self, id_bookmark: str, data: dict) -> Union[bool, str]:
        ''' Atualiza os campos de um bookmark. 

        Os únicos atualmente aceitos de serem alterados é o nome do bookmark e a pasta em que
        ele está, alterando seu ID.

        Args:
            - id_bookmark: Identificador único do bookmark a ser alterado.
            - data: dicionário com os campos e valores de um dicionário a ser alterado.

        Returns:
            Retorna uma tupla. Onde a primeira posição é `False` se há algum erro ou dado
            inválido foi encontrado durante a alteração do bookmark, junto com um respectiva
            mensagem de erro na segunda posíção. 

            Caso tudo tenha ocorrido corretamente, a tupla terá a primeira posição igual a 
            `True`, e a segunda posição com um string vazia. 

        '''
        
        bookmark = self.get(id_bookmark)
        if bookmark is None:
            return False, 'Verifique se o ID informado é válido!' 

        del bookmark['id']

        updated_bookmark = bookmark.copy()
        for field in data:

            if field == 'nome':
                updated_bookmark[field] = data[field]

            elif field == 'id_pasta':
                old_folder_id = bookmark[field]
                success = self.bookmark_folder.remove_file(old_folder_id, id_bookmark)
                if not success:
                    return False, 'Não foi possível remover o bookmark de sua pasta antiga'
                updated_bookmark[field] = data[field]

            else:
                return False, f'Não é possível atualizar o campo "{field}"'

        if updated_bookmark == bookmark:
            return False, 'O bookmark já está atualizado!'

        response = self.es.update(index=self.index_name, id=id_bookmark, body={"doc": updated_bookmark})
        
        success = response['result'] == 'updated' 
        msg_error = '' if success else 'Não foi possível atualizar o bookmark'

        return success, msg_error