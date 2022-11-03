import json
from copy import deepcopy
import json
from tqdm import tqdm
from nltk.corpus import stopwords
stopwords = stopwords.words("portuguese")


if __name__ == "__main__":
    REVIEWERS_NUMBER = 4
    ENTRIES_PER_REVIEWER = 2
    #distribuição e coloração das entradas
    with open(f"./data/feedback_queries_final.json", "r") as input_file:
        feedback_data_final = eval(input_file.read())

    feedback = {f"reviewer_{idx}": [] for idx in range(REVIEWERS_NUMBER)}

    for idx, entry in enumerate(feedback_data_final):
        #revisar essa lógica
        value = idx % ENTRIES_PER_REVIEWER
        feedback[f"reviewer_{value}"].append(entry)
        feedback[f"reviewer_{value + ENTRIES_PER_REVIEWER}"].append(entry)

    # coloring
    with open("./data/generated_queries.txt", "r") as queries_file:
        queries = eval(queries_file.read())

    # styles
    style_list = [
        'style="color:white;background-color:gray;"',
        'style="color:white;background-color:blue;"',
        'style="color:white;background-color:green;"',
        'style="color:black;background-color:yellow;"',
        'style="color:white;background-color:brown;"',
        'style="color:black;background-color:orange;"',
        'style="color:white;background-color:red;"',
        'style="color:black;background-color:pink;"',
        'style="color:white;background-color:purple;"',
    ]

    for person, data_list in feedback.items():
        for entry in data_list:
            new_corresponding = ""
            query_tokens = entry["query"].lower().split()
            query_tokens = [token for token in query_tokens if not token in stopwords]
            color_codes = dict(zip(query_tokens, style_list[:len(query_tokens)]))
            for corres in entry["corresponding"]:
                for token in corres["text"].split():
                    if token.lower() in query_tokens:
                        new_corresponding += f"<mark {color_codes[token.lower()]}>" + token + "</mark> "
                    else:
                        new_corresponding += token + " "
                corres["formatted_text"] = new_corresponding

            entry["formatted_text"] = "<br>"
            for token in entry["query"].split():
                if token in query_tokens:
                    entry["formatted_text"] += f"<mark {color_codes[token]}>" + token + "</mark> "
                else:
                    entry["formatted_text"] += token + " "

    #saving
    for person, data_list in feedback.items():
        with open(f"./data/feedback_{person}.json", "w") as output:
            output.write(json.dumps(data_list, ensure_ascii=False))
