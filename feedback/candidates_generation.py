import requests
import random
import json
from tqdm import tqdm
import requests

def format_text(text):
    import re
    text = re.sub('\n+', '\n', text)
    return text.replace("\n", " ")

def apply_similarity(method):
    print(requests.post("http://localhost:9200/_all/_close?wait_for_active_shards=0&pretty").json())
    method = "BM25" if method == "dense" or method == "bm25sparse" else "LMDirichlet"
    data = json.dumps({"index": {"similarity": {"default": {"type": f"{method}"}}}})
    print(requests.put("http://localhost:9200/_all/_settings?pretty", headers={"Content-Type": "application/json"}, data=data).json())
    print(requests.post("http://localhost:9200/_all/_open?pretty").json())


if __name__ == "__main__":
    with open("./data/generated_queries.txt", "r") as queries_file:
        queries = eval(queries_file.read())
    random.shuffle(queries)

    ## Submete consultas
    for strategy in ["dense", "bm25sparse", "dirisparse"]:
        apply_similarity(strategy)
        feedback_data = []
        for q in tqdm(queries):
            try:
                query = q["query"].replace("/", "")
                params = {'consulta': query,  'page': 1, 'sid': '123'}
                service_response = requests.get('http://localhost:8000/services/search', params)
                results = json.loads(service_response.text)
                feedback_line = {}
                feedback_line["text"] = query
                feedback_line["_id"] = q["id"]
                feedback_line["corresponding"] = []
                # seleciona os 2 primeiros de cada estratégia
                results = sorted(json.loads(service_response.text)["documentos"], key=lambda x: x["posicao_ranking"])
                if not len(results):
                    print("e", len(results))
                for row in results:
                    feedback_line["corresponding"].append({"text": row["conteudo"].encode('utf-8').decode("utf-8"), "_id": row["id"]})
                feedback_data.append(feedback_line)
            except Exception as err:
                print(err)
                continue

        with open(f"./data/feedback_queries_{strategy}.json", "w") as output:
            output.write(json.dumps(feedback_data, ensure_ascii=False))

    ## Merge rankings
    with open(f"./data/feedback_queries_dense.json", "r") as input_file:
        feedback_data_dense = eval(input_file.read())
    with open(f"./data/feedback_queries_dirisparse.json", "r") as input_file:
        feedback_data_dirisparse = eval(input_file.read())
    with open(f"./data/feedback_queries_bm25sparse.json", "r") as input_file:
        feedback_data_bm25sparse = eval(input_file.read())

    feedback_data_dense_dict = {}
    for line in feedback_data_dense:
        feedback_data_dense_dict[line["text"]] = line

    feedback_data_dirisparse_dict = {}
    for line in feedback_data_dirisparse:
        feedback_data_dirisparse_dict[line["text"]] = line

    feedback_data_bm25sparse_dict = {}
    for line in feedback_data_bm25sparse:
        feedback_data_bm25sparse_dict[line["text"]] = line

    feedback_data_final = []
    for q in tqdm(queries):
        try:
            query = q["query"].replace("/", "")

            feedback_line = {}
            feedback_line["text"] = "CONSULTA: " + query
            feedback_line["query"] = query
            feedback_line["_id"] = q["id"]
            feedback_line["corresponding"] = []
            counter = 0
            included = []
            max_candidate = 0

            for origin, feedback_list in zip(["dense", "dirisparse", "bm25sparse"], [feedback_data_dense_dict, feedback_data_dirisparse_dict, feedback_data_bm25sparse_dict]):
                max_candidate+= len(feedback_list[query]["corresponding"])
            if max_candidate < 6:
                continue

            #combina os corresponding de cada estratégia
            while len(feedback_line["corresponding"]) < 6:
                counter = 0
                for origin, feedback_list in zip(["dense", "dirisparse", "bm25sparse"], [feedback_data_dense_dict, feedback_data_dirisparse_dict, feedback_data_bm25sparse_dict]):
                    for entry in feedback_list[query]["corresponding"]:
                        # incluir a posição do elemento naquele ranking de origem
                        if query + "--" + entry["_id"] in included:
                            continue
                        if counter == 2:
                            counter = 0
                            break
                        entry["text"] = format_text(entry["text"])
                        entry["origin"] = origin
                        feedback_line["corresponding"].append(entry)
                        counter+= 1
                        included.append(query + "--" + entry["_id"])
            feedback_data_final.append(feedback_line)
        except Exception as err:
            print(err)
            continue

    with open(f"./data/feedback_queries_final.json", "w") as output:
        output.write(json.dumps(feedback_data_final, ensure_ascii=False))
