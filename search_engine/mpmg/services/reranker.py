from time import sleep

from sentence_transformers import SentenceTransformer, models
from torch import nn
from scipy import spatial


class Reranker():
    def __init__(self):
        self.model = self.get_sentence_model()
    
    def get_sentence_model(self, model_path="prajjwal1/bert-tiny"):
        word_embedding_model = models.Transformer(model_path, max_seq_length=500)
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())

        return SentenceTransformer(modules=[word_embedding_model, pooling_model])

    def get_bert_score(self, embedding_vector, query_vector, n=5):
        return 1 - spatial.distance.cosine(embedding_vector, query_vector)

    def rerank(self, text_query, documents):
        query_vector = self.model.encode(text_query)

        for document in documents:
            document.score = self.get_bert_score(document.embedding_vector, query_vector)

        documents = sorted(documents, reverse=True, key=lambda doc: doc.score)
        return documents