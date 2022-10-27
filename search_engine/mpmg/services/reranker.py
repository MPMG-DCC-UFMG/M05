
from scipy import spatial
from .semantic_model import SemanticModel

class Reranker():
    def __init__(self):
        self.semantic_model = SemanticModel()
    
    def get_bert_score(self, embedding, query_embedding, n=5):
        return 1 - spatial.distance.cosine(embedding, query_embedding)

    def rerank(self, text_query, documents):
        query_embedding = self.semantic_model.get_dense_vector(text_query)
        # query_embedding = self.semantic_model.ge .encode(text_query)
        for document in documents:
            document['score'] = self.get_bert_score(document.embedding, query_embedding)        
        
        documents.sort(key=lambda doc: doc['score'], reverse=True)
        for ranking_position, document in enumerate(documents, 1):
            document['posicao_ranking'] = ranking_position

        return documents