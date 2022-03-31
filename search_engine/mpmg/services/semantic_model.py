from sentence_transformers import SentenceTransformer, models


class SemanticModel:

    def __init__(self, model_path="neuralmind/bert-base-portuguese-cased", max_seq_length=500):
        super().__init__()
        self.model_path = model_path
        self.max_seq_length = max_seq_length
        self.word_embedding_model = models.Transformer(model_path, max_seq_length)
        self.pooling_model = models.Pooling(self.word_embedding_model.get_word_embedding_dimension())
        self.sentence_model = SentenceTransformer(modules=[self.word_embedding_model, self.pooling_model])


    def get_dense_vector(self, text):
        return self.sentence_model.encode(text)
        