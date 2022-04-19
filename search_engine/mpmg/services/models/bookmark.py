import hashlib

from mpmg.services.models import ElasticModel
from mpmg.services.models.bookmark_folder import BookmarkFolder
from mpmg.services.utils import doc_filter

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

    def generate_id(self, id_usuario: str, indice_documento: str, id_documento: str) -> str:
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

    def get_all(self, user_id: str) -> dict:
        '''Retorna todas as pastas do usuário user_id estruturado como uma árvore de pastas.

        Args:
            - user_id: ID do usuário que terá sua árvore de pastas gerada.

        Returns:
            Retorna um dicionário estruturado como uma árvore de pastas.

        '''
        bookmarks_found = doc_filter(self.index_name, {'term': {'id_usuario.keyword': user_id}})
         
        bookmarks = list()
        for bookmark_found in bookmarks_found:
            bookmarks.append({'id': bookmark_found['_id'], **bookmark_found['_source']})
        
        return bookmarks
