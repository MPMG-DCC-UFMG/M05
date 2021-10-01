import subprocess
import json

from django.conf import settings
from mpmg.services. models import SearchableIndicesConfigs

class NER:
    '''
    Classe responsável por interagir com o modelo reconhecedor de entidades.
    Por enquanto copiamos o modelo JAVA para dentro do projeto e esta classe
    o executa. No futuro este modelo funcionará como um serviço e esta classe
    irá apenas fazer requisições para o serviço.
    '''

    ner_args = ['java', '-cp', 'mp-ufmg-ner.jar:lib/*', 'Pipeline', '-str'] 
    ner_dir = settings.NER_DIR

        
    def execute(cls, text):
        '''
        Reconhece entidades no texto fornecido e retorna um dicionário relacionando
        o campo do índice de acordo com o tipo da entidade e a lista de entidades
        reconhecidas no texto. 
        '''

        args = cls.ner_args + [text]
        out, err = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=cls.ner_dir).communicate()
        ner_data = json.loads(out.decode('utf-8'))

        entities = {}
        for line in ner_data['entities']:
            field = settings.ENTITY_TYPE_TO_INDEX_FIELD[line['label']]
            if field not in entities:
                entities[field] = set()
            entities[field].add(line['entity'])
        
        for field in entities:
            entities[field] = list(entities[field])
        
        return entities


