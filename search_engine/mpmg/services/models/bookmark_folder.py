from datetime import datetime
from elasticsearch.exceptions import NotFoundError

from mpmg.services.elastic import Elastic
from mpmg.services.models.elastic_model import ElasticModel

class BookmarkFolder(ElasticModel):
    index_name = 'bookmark_folder'

    def __init__(self, **kwargs):
        index_name = BookmarkFolder.index_name
        meta_fields = ['id']
        index_fields = [
            'criador',
            'nome',
            'data_criacao',
            'data_modificacao',
            'data_ultimo_arquivo_adicionado',
            'pasta_pai',
            'subpastas',
            'arquivos'
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def save(self, dict_data=None):
        if dict_data == None:
            dict_data = {}
            for field in self.index_fields:
                dict_data[field] = getattr(self, field, '')

        if self.get_item(dict_data['pasta_pai']) is None:
            return None 

        dict_data['data_criacao'] = datetime.now().timestamp()
        dict_data['data_modificacao'] = datetime.now().timestamp()
        dict_data['data_ultimo_arquivo_adicionado'] = None  

        es = Elastic().es
        result = es.index(index=self.index_name, body=dict_data)
        
        self.add_children(dict_data['pasta_pai'], result['_id'])

        return result['_id']

    # Cria a pasta raiz do usuário, se ela não tiver sido criada
    def create_default_bookmark_folder_if_necessary(self, user_id):
        try:
            Elastic().es.get(index=self.index_name, id=user_id)
        
        except NotFoundError:
            data = dict(
                criador=str(user_id),
                nome='Favoritos',
                data_criacao=datetime.now().timestamp(),
                data_modificacao=datetime.now().timestamp(),
                data_ultimo_arquivo_adicionado = None,
                pasta_pai=None,
                subpastas=[],
                arquivos=[]
            )

            Elastic().es.index(index=self.index_name, id=user_id, body=data)
        
    def get_item(self, folder_id):
        try:
            response = Elastic().es.get(index=self.index_name, id=folder_id) 
            item = {'id': response['_id'], **response['_source']}
            return item        

        except:
            return None

    def rename(self, folder_id, new_name):
        try:

            data = {
                "nome": new_name,
                "data_modificacao": datetime.now().timestamp()
            }

            response = Elastic().es.update(index=self.index_name, id=folder_id, body={"doc": data})

            return response['result'] == 'updated'

        except:
            return False 

    def add_file(self, folder_id, file_id):
        
        try:
            folder = self.get_item(folder_id)
            
            folder['arquivos'].append(file_id)

            now = datetime.now().timestamp()
            data = {
                "arquivos": folder['arquivos'],
                "data_modificacao": now,
                "data_ultimo_arquivo_adicionado": now  

            }
            
            response = Elastic().es.update(index=self.index_name, id=folder_id, body={"doc": data})
            
            return response['result'] == 'updated'
        
        except:
            return False 

    def remove_file(self, folder_id, file_id):
        try:
            folder = self.get_item(folder_id)

            folder['arquivos'].remove(file_id)

            data = {
                "arquivos": folder['arquivos'],
                "data_modificacao": datetime.now().timestamp()
            }
            
            response = Elastic().es.update(index=self.index_name, id=folder_id, body={"doc": data})

            return response['result'] == 'updated'
        
        except:
            return False

    def add_children(self, parent_id, children_id):
        try:
            parent_folder = self.get_item(parent_id)
            
            parent_folder['subpastas'].append(children_id)
            
            data = {
                "subpastas": parent_folder['subpastas'],
                "data_modificacao": datetime.now().timestamp()
            }
            
            response = Elastic().es.update(index=self.index_name, id=parent_id, body={"doc": data})

            return response['result'] == 'updated'

        except:
            return False 

    def remove_children(self, parent_id, children_id):
        try:
            parent_folder = self.get_item(parent_id)
            
            parent_folder['subpastas'].remove(children_id)
            
            data = {
                "subpastas": parent_folder['subpastas'],
                "data_modificacao": datetime.now().timestamp()
            }

            response = Elastic().es.update(index=self.index_name, id=parent_id, body={"doc": data})

            return response['result'] == 'updated'
        
        except:
            return False 

    def remove_tree(self, tree_id):
        folder = self.get_item(tree_id)

        for subfolder_id in folder['subpastas']:
            self.remove_tree(subfolder_id)

        Elastic().es.delete(index=self.index_name, id=tree_id)

    def remove_folder(self, folder_id, decision):
        try:
            folder = self.get_item(folder_id)
            pasta_pai = folder['pasta_pai']

            self.remove_children(pasta_pai, folder_id)

            if decision == 'remove_all':
                self.remove_tree(folder_id) 

            return True
        
        except:
            return False 

    def get_folder_tree(self, root_id) -> dict:
        folder = self.get_item(root_id)

        subpastas = []
        for subfolder_id in folder['subpastas']:
            subpastas.append(self.get_folder_tree(subfolder_id))

        folder['subpastas'] = subpastas
        return folder 