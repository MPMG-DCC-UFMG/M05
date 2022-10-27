class SemanticModel:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            from sentence_transformers import SentenceTransformer, models
            
            print('Creating new instance')
            cls.instance = super(SemanticModel, cls).__new__(cls)

            model_path = 'prajjwal1/bert-tiny'
            max_seq_length=500

            word_embedding_model = models.Transformer(model_path, max_seq_length)
            pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
            cls.instance.sentence_model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
        
        else:
            print('Already exists a instance')

        return cls.instance
        
    def get_dense_vector(self, text):
        return self.sentence_model.encode(text)
        