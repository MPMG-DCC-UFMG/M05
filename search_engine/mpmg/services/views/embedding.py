from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sentence_transformers import SentenceTransformer, models
from ..docstring_schema import AutoDocstringSchema
import numpy as np

class EmbeddingView(APIView):
    '''
    get:
      description: Retorna o vetor de embeddings representando o texto passado como parâmetro.
      parameters:
        - name: text_contents
          in: query
          description: Conteúdo textual a ser transformado
          required: true
          schema:
            type: array
            items:
              type: string
    '''

    schema = AutoDocstringSchema()

    def get(self, request):
        text_contents = request.GET.getlist('text_contents')

        model_path="neuralmind/bert-base-portuguese-cased"
        word_embedding_model = models.Transformer(model_path, max_seq_length=500)
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())

        sentence_model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

        embedding_vectors = []
        for text in text_contents:
            embedding_vectors.append(self._change_vector_precision(self._get_dense_vector(sentence_model, text)))

        return Response({
                'embedding_vectors': embedding_vectors
            })
    

    def _get_dense_vector(self, model, text_list):
        vectors = model.encode([text_list])
        vectors = [vec.tolist() for vec in vectors]
        return vectors[0]
    
    def _change_vector_precision(self, vector, precision=24):
        vector = np.array(vector, dtype=np.float16)
        return vector.tolist()