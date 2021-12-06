from datetime import date, datetime
from elasticsearch.exceptions import NotFoundError

from mpmg.services.elastic import Elastic
# from mpmg.services.models.bookmark import Bookmark
from mpmg.services.models.elastic_model import ElasticModel

from typing import Callable, Dict, Tuple, Union, List

class BookmarkFolder(ElasticModel):
    
    index_name = 'bookmark_folder'
    es = Elastic().es
    
    def __init__(self, **kwargs):
        index_name = BookmarkFolder.index_name
        meta_fields = ['id']
        index_fields = [
            'criador',
            'nome',
            'data_criacao',
            'data_modificacao',
            'pasta_pai',
            'subpastas',
            'arquivos'
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def save(self, dict_data=None) -> Tuple[str, str]:
        ''' Salva a pasta de bookmarks no índice. 
        
        Chaves passadas em dict_data que não estiverem especificadas em index_fields serão ignoradas. 
        Se dict_data for igual a None, os atributos do objeto é que serão salvos.
        
        Args:
            - dict_data: Representa os valores a serem salvos. Chaves passadas em dict_data que não 
                        estiverem especificadas em index_fields serão ignoradas. Se dict_data 
                        for igual a None, os atributos do objeto é que serão salvos.

        Returns:
            Retorna uma tupla com a primeira posição sendo uma string com ID do bookmark criado 
            ou um string vazia, se não foi possível criá-lo junto com um mensagem de erro.
        '''
        
        if dict_data == None:
            dict_data = {}
            for field in self.index_fields:
                dict_data[field] = getattr(self, field, '')

        if self.get(dict_data['pasta_pai']) is None:
            return '', f'A pasta pai de ID {dict_data["pasta_pai"]} não existe ou não foi possível obtê-la.' 
        
        now = datetime.now().timestamp()

        dict_data['data_criacao'] = now
        dict_data['data_modificacao'] = now

        response = self.es.index(index=self.index_name, body=dict_data)
        
        if response['result'] != 'created':
            return '', f'Não foi possível criar a pasta "{dict_data["nome"]}"". Tente novamente!'

        result = self.add_subfolder(dict_data['pasta_pai'], response['_id'])
        if not result:
            self.es.delete(index=self.index_name, id=response['_id'])
            return '', f'Falha ao adicionar a pasta "{dict_data["nome"]}" como subpasta da pasta de ID {dict_data["pasta_pai"]}'

        return response['_id'], ''

    def _undo_operations(self, undo_queue: List[Tuple[Callable, Dict]]):
        '''Desfaz
        
        '''

        for undo_method, arg in undo_queue:
            undo_method(**arg)

    def update(self, folder_id: str, data: dict) -> Tuple[bool, str]:
        folder = self.get(folder_id)
        if folder is None:
            return False, f'A pasta de ID informado não existe!'

        del folder['id']

        updated_folder = folder.copy()
        undo_queue = list()
        
        for field in data:
            if field == 'nome':
                updated_folder[field] = data[field]
            
            elif field == 'pasta_pai':
                # move folder
                old_parent_folder = folder['pasta_pai']

                success = self.remove_subfolder(old_parent_folder, folder_id)
                if not success:
                    self._undo_operations(undo_queue)
                    return False, f'Não foi possível atualizar a antiga pasta pai que a pasta de ID {folder_id} está sendo movida.'
                
                undo_queue.append((self.add_subfolder, {'parent_id': old_parent_folder, 'children_id': folder_id}))
                
                new_parent_folder = data['pasta_pai']
                success = self.add_subfolder(new_parent_folder, folder_id)

                if not success:
                    self._undo_operations(undo_queue)
                    return False, f'Não foi possível atualizar a pasta de destino que a pasta de ID {folder_id} foi movida para ela.'
                
                undo_queue.append((self.remove_subfolder, {'parent_id': new_parent_folder, 'children_id': folder_id}))
                updated_folder['pasta_pai'] = new_parent_folder
            
            elif field == 'subpastas':
                updated_folder['subpastas'] = data['subpastas']
                 
            elif field == 'arquivos':
                updated_folder['arquivos'] = data['arquivos']

            else:
                return False, f'Não é possível alterar o campo "{field}" na pasta!'
        
        if updated_folder == folder:
            return False, 'Não há alterações a serem feitas!'

        updated_folder['data_modificacao'] = datetime.now().timestamp()

        response = self.es.update(index=self.index_name, 
                                        id=folder_id, 
                                        body={"doc": updated_folder})

        success = response['result'] == 'updated'
        if not success:
            self._undo_operations(undo_queue)

        msg_error = '' if success else 'Não possível atualizar a pasta. Tente novamente!'

        return success, msg_error

    # Cria a pasta raiz do usuário, se ela não tiver sido criada
    def create_default_bookmark_folder_if_necessary(self, user_id) -> None:
        try:
            self.es.get(index=self.index_name, id=user_id)
        
        except NotFoundError:
            now = datetime.now().timestamp()
            
            data = dict(
                criador=str(user_id),
                nome='Favoritos',
                pasta_pai=None,
                data_criacao = now,
                data_modificacao = now,
                subpastas=[],
                arquivos=[]
            )
        
            res = self.es.index(index=self.index_name, body=data, id=user_id)

    def get(self, folder_id: str) -> Union[Dict, None]:
        try:
            response = self.es.get(index=self.index_name, id=folder_id) 
            item = {'id': response['_id'], **response['_source']}
            return item        

        except:
            return None

    def add_file(self, folder_id, file_id) -> bool:
        
        try:
            folder = self.get(folder_id)
            
            folder['arquivos'].append(file_id)

            now = datetime.now().timestamp()
            data = {
                "arquivos": folder['arquivos'],
                "data_modificacao": now,
                "data_ultimo_arquivo_adicionado": now  

            }
            
            response = self.es.update(index=self.index_name, id=folder_id, body={"doc": data})
            
            return response['result'] == 'updated'
        
        except:
            return False 

    def remove_file(self, folder_id, file_id) -> bool:
        try:
            folder = self.get(folder_id)

            folder['arquivos'].remove(file_id)

            data = {
                "arquivos": folder['arquivos'],
                "data_modificacao": datetime.now().timestamp()
            }
            
            response = self.es.update(index=self.index_name, id=folder_id, body={"doc": data})

            return response['result'] == 'updated'
        
        except:
            return False

    def add_subfolder(self, parent_id, children_id):
        try:
            parent_folder = self.get(parent_id)
            
            parent_folder['subpastas'].append(children_id)
            
            data = {
                "subpastas": parent_folder['subpastas'],
                "data_modificacao": datetime.now().timestamp()
            }
            
            response = self.es.update(index=self.index_name, id=parent_id, body={"doc": data})

            return response['result'] == 'updated'

        except:
            return False 

    def remove_subfolder(self, parent_id, children_id):
        try:
            parent_folder = self.get(parent_id)
            parent_folder['subpastas'].remove(children_id)
            
            data = {
                "subpastas": parent_folder['subpastas'],
                "data_modificacao": datetime.now().timestamp()
            }

            response = self.es.update(index=self.index_name, id=parent_id, body={"doc": data})
            return response['result'] == 'updated'
        
        except:
            return False 

    def remove_tree(self, tree_id, bookmark_handler):
        folder = self.get(tree_id)

        for file_id in folder['arquivos']:
            self.es.delete(index=bookmark_handler.index_name, id=file_id)

        for subfolder_id in folder['subpastas']:
            self.remove_tree(subfolder_id)

        self.es.delete(index=self.index_name, id=tree_id)

    def remove_folder(self, folder_id, bookmark_handler):
        try:
            folder = self.get(folder_id)
            pasta_pai = folder['pasta_pai']

            self.remove_subfolder(pasta_pai, folder_id)
            self.remove_tree(folder_id, bookmark_handler) 

            return True
        
        except:
            return False 

    def get_folder_tree(self, root_id) -> dict:
        folder = self.get(root_id)

        subpastas = []
        for subfolder_id in folder['subpastas']:
            subpastas.append(self.get_folder_tree(subfolder_id))

        folder['subpastas'] = subpastas
        return folder 