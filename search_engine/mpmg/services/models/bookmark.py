import hashlib
from typing import Union
from elasticsearch.transport import get_host_info
from elasticsearch_dsl.aggs import Pipeline
from rest_framework import response

from rest_framework.response import Response
from aduna.views import bookmark

from mpmg.services.elastic import Elastic
from mpmg.services.models import ElasticModel
from mpmg.services.models.bookmark_folder import BookmarkFolder

from typing import Callable, Dict, Tuple, Union, List

class Bookmark(ElasticModel):
    index_name = 'bookmark'
    bookmark_folder = BookmarkFolder() 

    def __init__(self, **kwargs):
        index_name = Bookmark.index_name
        meta_fields = ['id']
        index_fields = [
            'id_pasta',
            'id_usuario',
            'indice_documento',
            'id_documento',
            'id_consulta',
            'id_sessao',
            'nome',
            'data_criacao',
            'data_modificacao',
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def get_id(self, id_usuario: str, indice_documento: str, id_documento: str) -> str:
        '''Retorna o ID de um bookmark, baseado em seu ID, no índice e ID do documento que ele registra.

        Args:
            - id_usuario: ID do usuário que criou o bookmark.
            - indice_documento: Índice do documento a ser salvo pelo bookmark.
            - id_documento: ID do documento a ser salvo pelo bookmark.

        Returns:
            Retorna o ID de um bookmark, baseado na hash SHA-1 do índice e ID do documento que ele salva.

        '''
        key = id_usuario + indice_documento + id_documento
        return hashlib.sha1(key.encode()).hexdigest()

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

        if self.bookmark_folder.get(dict_data['id_pasta']) is None:
            return None 

        id_usuario = dict_data['id_usuario'] 
        indice_documento = dict_data['indice_documento'] 
        id_documento = dict_data['id_documento']

        bookmark_id = self.get_id(id_usuario, indice_documento, id_documento)

        if self.get(bookmark_id):
            return None

        result = self.elastic.es.index(index=self.index_name, id=bookmark_id, body=dict_data)

        self.bookmark_folder.add_file(dict_data['id_pasta'], result['_id'])

        return bookmark_id


    def get(self, id_bookmark: str) -> Union[dict, None]:
        ''' Recupa um bookmar por seu ID id_bookmark.

        Args:
            - id_bookmark: ID do bookmark a ser recuperado.

        Returns:
            Retorna um dicionário representando o bookmark, ou None, se não foi possível recuperá-lo.
        '''
        
        try:
            data = self.elastic.es.get(index=self.index_name, id=id_bookmark)['_source']        
            data['id'] = id_bookmark
            return data
            
        except:
            return None

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
        success = self.bookmark_folder.remove_file(id_pasta, id_bookmark)
        
        if not success:
            return False, 'Não foi possível remover o bookmark de sua pasta!'

        response = self.elastic.es.delete(index=self.index_name, id=id_bookmark)
        success = response['result'] == 'deleted'

        msg_error = ''
        if not success:
            msg_error = 'Não foi possível remover o bookmark!'
            self.bookmark_folder.add_file(id_pasta, id_bookmark)

        return success, msg_error
    
    def _undo_operations(self, undo_queue: List[Tuple[Callable, Dict]]):
        '''Desfaz
        
        '''

        for undo_method, arg in undo_queue:
            undo_method(**arg)

    def update(self, bookmark_id: str, data: dict) -> Union[bool, str]:
        ''' Atualiza os campos de um bookmark. 

        Os únicos atualmente aceitos de serem alterados é o nome do bookmark e a pasta em que
        ele está, alterando seu ID.

        Args:
            - bookmark_id: Identificador único do bookmark a ser alterado.
            - data: dicionário com os campos e valores de um dicionário a ser alterado.

        Returns:
            Retorna uma tupla. Onde a primeira posição é `False` se há algum erro ou dado
            inválido foi encontrado durante a alteração do bookmark, junto com um respectiva
            mensagem de erro na segunda posíção. 

            Caso tudo tenha ocorrido corretamente, a tupla terá a primeira posição igual a 
            `True`, e a segunda posição com um string vazia. 

        '''
        
        bookmark = self.get(bookmark_id)
        if bookmark is None:
            return False, 'Verifique se o ID informado é válido!' 

        del bookmark['id']

        undo_queue = list()
        updated_bookmark = bookmark.copy()
        for field in data:

            if field == 'name':
                updated_bookmark['nome'] = data[field]

            elif field == 'folder_id':
                old_folder_id = bookmark['id_pasta']
                success = self.bookmark_folder.remove_file(old_folder_id, bookmark_id)
                if not success:
                    self._undo_operations(undo_queue)
                    return False, 'Não foi possível remover o bookmark de sua pasta antiga.'

                undo_queue.append((self.bookmark_folder.add_file, {'folder_id': old_folder_id, 'file_id': bookmark_id}))
                
                new_folder_id = data['folder_id']
                success = self.bookmark_folder.add_file(new_folder_id, bookmark_id)

                if not success:
                    self._undo_operations(undo_queue)
                    return False, 'Não foi possível inserir o bookmark na nova pasta.'

                undo_queue.append((self.bookmark_folder.remove_file, {'folder_id': new_folder_id, 'file_id': bookmark_id}))

                updated_bookmark['id_pasta'] = data[field]

            else:
                return False, f'Não é possível atualizar o campo "{field}"'

        if updated_bookmark == bookmark:
            return False, 'O bookmark já está atualizado!'

        response = self.elastic.es.update(index=self.index_name, id=bookmark_id, body={"doc": updated_bookmark})
        
        success = response['result'] == 'updated' 
        msg_error = ''
        if not success:
            self._undo_operations(undo_queue)
            msg_error = 'Não foi possível atualizar o bookmark'

        return success, msg_error

    def get_all(self, user_id: str) -> list:
        # esse é provavelmente o método mais eficiente de recuperar 
        results = list()
        for bookmark_id in self.bookmark_folder.get_all_files_id(user_id):
            results.append(self.get(bookmark_id))
        return results