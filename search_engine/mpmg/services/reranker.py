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

    def get_bert_score(self, sentence_vectors, query_vector, n=5):
        similarities = []

        for sentence_vector in sentence_vectors:
            value = 1 - spatial.distance.cosine(sentence_vector["vector"], query_vector)
            similarities.append(value)

        similarities = sorted(similarities)[-n:]
        score = sum(similarities)
        return score

    def rerank(self, text_query, documents):
        query_vector = self.model.encode(text_query)

        for document in documents:
            document.score = self.get_bert_score(document.sentences_vectors, query_vector)

        documents = sorted(documents, reverse=True, key=lambda doc: doc.score)
        return documents