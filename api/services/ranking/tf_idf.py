from collections import OrderedDict

class TF_IDF:
    def __init__(self, initial_ranking, features):
        self.initial_ranking = initial_ranking
        self.features = features
        self.new_ranking = []
    
    def reranking(self):
        for hit in self.initial_ranking:
            score = 0.0
            id_ = hit.meta.id
            for field, field_info in self.features[id_].items():
                for term, term_info in field_info['matched_terms'].items():
                    score += term_info['tf'] * term_info['idf']
            self.new_ranking.append({'hit':hit, 'new_score':score})
        
        self.new_ranking = sorted(self.new_ranking, key=lambda item: item['new_score'], reverse=True)
        
        # for item in self.new_ranking:
        #     print(item['hit'].meta.id, item['hit'].meta.score, item['new_score'])
        
        return self.new_ranking