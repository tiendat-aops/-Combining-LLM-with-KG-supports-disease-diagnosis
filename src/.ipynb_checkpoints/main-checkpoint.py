import os
from utils import write_to_txt, extract_zip
from pdf_file import PdfFile
from chunking import get_chunks
from utils import write_to_csv
from remove_stopword import remove_stopword
import spacy
from tqdm import tqdm
from preprocess import preprocess, count_keyword, load_entity, create_dict_name_mean, create_dict_name_processed_name, convert_list_content_to_list_word
from cal_interact_value import cal_interaction_value, softmax
from split_content import get_all_content, chunk_content, sentence_split, get_all_content_by_pages
import csv
from transformers import HfArgumentParser
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
from hypothesis_test import hypothesis_test
from tf_idf import tf_idf, term_frequency
import numpy as np

@dataclass
class RunningArguments:
    subject_type: Optional[str] = field(
        default = "symptoms",
        metadata = {"help": "Define type of subject to calculate scores."}
    )
    object_type: Optional[str] = field(
        default = "disease",
        metadata = {"help": "Define type of object to calculate scores."}
    )
    limit_num_occur: Optional[int] = field(
        default = 0,
        metadata = {"help": "Delete entities that occurs less than n times."}
    )
    n_chunking: Optional[int] = field(
        default = 50,
        metadata = {"help": "Define number of chunking to calculate scores."}
    )
    data_genre: Optional[str] = field(
        default = "all",
        metadata = {"help" : "Genre of data want to calculate."},
    )
    alpha: Optional[float] = field(
        default = 1,
        metadata = {"help": "Hyperparameter for Laplacian function"}
    )
    signigicant_value: Optional[float] = field(
        default = 0.05,
        metadata = {"help": "Significant values for hypothesis testing."}
    )
    min_score: Optional[float] = field(
        default = 0.1,
        metadata = {"help": "Remove link if scores between entities less than min_score"}
    )
    func_option: Optional[str] = field(
        default = "org",
        metadata = {"help": "function to Calculate interaction score"}
    )
    run_option: Optional[str] = field(
        default = "calculation_score"
    )
def get_args():
    parser = HfArgumentParser(RunningArguments)
            
    run_args, = parser.parse_args_into_dataclasses()
    # Optionally, show a warning on unknown arguments.
    return run_args

def run_hypothesis_test(file_path, entities_path, labels, run_args):
    dict_name_mean = create_dict_name_mean(entities_path = entities_path, label = 'all')
    dict_name_processed_name = create_dict_name_processed_name(entities_path = entities_path, label = 'all')
    output_path = entities_path = os.path.join(file_path, f"keyword/{labels[0]}_{labels[1]}")
    scores_dict = {}
    dict_number_link = {}
    for i in range(run_args.n_chunking):
        file_csv_path = os.path.join(output_path, f"score_{labels[0]}_{labels[1]}_chunk_{i}.csv")
        df = pd.read_csv(file_csv_path)
        for index, row in df.iterrows():
            key = (row[f"{labels[0]}"], row[f"{labels[1]}"])
            if key not in scores_dict:
                scores_dict[key] = []
                dict_number_link[key] = 0
            scores_dict[key].append(row['Score'])
            dict_number_link[key] += 1


    list_remove = []
    for key in scores_dict:
        scores = scores_dict[key]
        # print(scores)
        update_score = hypothesis_test(scores, sig_value=run_args.signigicant_value)
        if update_score < run_args.min_score:
            list_remove.append(key)
        else: scores_dict[key] = update_score
    for key in list_remove:
        del scores_dict[key]
    print(len(scores_dict))
    score_path = os.path.join(file_path, f"scores/scores_relationship.csv")
    score_path_vi = os.path.join(file_path, f"scores/scores_relationship_vi.csv")
    # Path to the CSV file
    # csv_file = 'data.csv'
    relationship = {('symptoms', 'disease'): 'symptom_of', ('disease', 'symptoms'): 'related_symptoms', ('disease', 'organ'): 'associated_with', ('organ', 'disease'): 'related_diseases', ('symptoms', 'organ'): 'symptom_of', ('organ', 'symptoms'): 'related_symptoms'}
    # Write data to CSV file
    relation = relationship[(f"{labels[0]}", f"{labels[1]}")]
    with open(score_path, 'a', newline='') as file:
        writer = csv.writer(file)
        # writer.writerow(['Subject', 'Object', 'Relationship', 'Score'])  # Write header
        for (subject, obj), score in scores_dict.items():
            writer.writerow([dict_name_processed_name[subject], dict_name_processed_name[obj], relation, score])
    with open(score_path_vi, 'a', newline='') as file:
        writer = csv.writer(file)
        # writer.writerow(['Subject', 'Object', 'Relationship', 'Score'])  # Write header
        for (subject, obj), score in scores_dict.items():
            writer.writerow([dict_name_mean[dict_name_processed_name[subject]], dict_name_mean[dict_name_processed_name[obj]], relation, score])

def run_calculation_scores(list_content, join_content, entities_path, file_path, labels, run_args):
    for i, content in enumerate(list_content):
        
        dict_keyword = {}
        for label in labels:
            key_entity, entity = load_entity(entities_path, label = label)
            number_key_entity = count_keyword(file_content = join_content[i], key_entity=key_entity, entity=entity, number_occur=run_args.limit_num_occur)
            dict_keyword[label] = number_key_entity
        # total = sum(my_dict.values())
        # rate_values = {key: value / total for key, value in my_dict.items()}

        
        output_file = os.path.join(file_path, f"keyword/{labels[0]}_{labels[1]}/score_{labels[0]}_{labels[1]}_chunk_{i}.csv")

        with open(output_file, 'w', newline = '') as file:
            header = [f"{labels[0]}", 'Score', f"{labels[1]}"]
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            for subject in tqdm(dict_keyword[f"{labels[0]}"]):
                for object in tqdm(dict_keyword[f"{labels[1]}"]):
                    if dict_keyword[f"{labels[1]}"][object] == 0:
                        score = 0
                        dict_res = {header[0]: subject, header[1]: score, header[2]: object}
                        writer.writerow(dict_res)
                        continue
                    elif dict_keyword[f"{labels[0]}"][subject] == 0:
                        score = 0
                        dict_res = {header[0]: subject, header[1]: score, header[2]: object}
                        writer.writerow(dict_res)
                        continue
                    else:
                        print("Start calulating..........\n")
                        score = cal_interaction_value(subject, object, content, run_args.alpha, function_option = run_args.func_option)
                        print("Doneeeeee\n")
                        dict_res = {header[0]: subject, header[1]: score, header[2]: object}
                        writer.writerow(dict_res)

def run_test_scores(subject, object, labels, list_content, run_args):
    # subject = ["hypertens", "pneumonia", "cirrhosi", "dementia", "carcinoma"]
    # object = ["heart", "lung", "liver", "brain", "cancer"]
    file = open("result.txt", "a")
    for s in subject:
        for o in object:
            list_scores_org = []
            list_scores_softmax = []
            list_scores_tf = []
            for i in tqdm(range(50)):
                if run_args.func_option == 'org':
                    score = cal_interaction_value(s, o, list_content[i], run_args.alpha, func_option = "org")
                    list_scores_org.append(score)
                    continue
                if run_args.func_option != 'org':
                    dict_keyword = {}
                    for label in labels:
                        key_entity, entity = load_entity(entities_path, label = label)
                        number_key_entity = count_keyword(file_content = join_content[i], key_entity=key_entity, entity=entity, number_occur=run_args.limit_num_occur)
                        dict_keyword[label] = number_key_entity
                if run_args.func_option == "tf":
                    total_subject = sum(dict_keyword[labels[0]].values())
                    total_object = sum(dict_keyword[labels[1]].values())

                    tf_subject = {key: value / total_subject for key, value in dict_keyword[labels[0]].items()}
                    tf_object = {key: value / total_object for key, value in dict_keyword[labels[1]].items()}

                    score_tf = cal_interaction_value(s, o, list_content[i], run_args.alpha, tf = tf_object[o] + tf_subject[s], func_option = "tf")
                    list_scores_tf.append(score_tf)

                if run_args.func_option == "softmax":
                    values_subject = np.array(list(dict_keyword[labels[0]].values()))
                    values_object = np.array(list(dict_keyword[labels[0]].values()))
                    rate_values_subject = softmax(values_subject)
                    rate_values_object = softmax(values_object)
            
                    
                    rate_dict_subject = {key: value for key, value in zip(dict_keyword[labels[0]].keys(), rate_values_subject)}
                    rate_dict_object = {key: value for key, value in zip(dict_keyword[labels[1]].keys(), rate_values_object)}
            
                    score_softmax = cal_interaction_value(s, o, list_content[i], run_args.alpha, tf = rate_dict_object[o] + rate_dict_subject[s], func_option = "softmax")
                    list_scores_softmax.append(score_softmax)
            if run_args.func_option == 'org':
                file.write(f"Result of {s} and {o} with the traditional caculation: \n")
                file.write(str(list_scores_org))
                file.write("\n")
                file.write(str(sum(list_scores_org)/len(list_scores_org)))
                file.write("\n")
                file.write(str(hypothesis_test(scores = list_scores_org, mean_hypo = 0, sig_value = 0.05)))
                file.write("\n--------------------------------------\n")
    # print(f"Result of {s} and {o} with the new calculation function: \n")
    # print(list_scores_tf)
    # print(sum(list_scores_tf)/len(list_scores_tf))
    # print(hypothesis_test(scores = list_scores_tf, mean_hypo = 0, sig_value = 0.05))
    # print("\n--------------------------------------\n")
    # print(f"Result of {s} and {o} with the softmax function: \n")
    # print(list_scores_softmax)
    # print(sum(list_scores_softmax)/len(list_scores_softmax))
    # print(hypothesis_test(scores = list_scores_softmax, mean_hypo = 0, sig_value = 0.05))
    # print("\n--------------------------------------\n")

def main():
    run_args = get_args()
    # define path
    file_path = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(file_path, "data")
    entities_path = os.path.join(file_path, "keyword/entities_final.csv")
    output_dir = os.path.join(file_path, "output")
    
    if run_args.data_genre == "all":
        output_name = "all_content_30_03.txt"
    elif run_args.data_genre == "shuffle":
        output_name = "all_content_13_04_shuffle_pages.txt"

    # Load content
    with open(f"{output_dir}/{output_name}", "r") as f:
        file_content = f.readlines()
    all_content = ' '.join(file_content)
    list_content, join_content = chunk_content(all_content, n_chunk=run_args.n_chunking)
    labels = [run_args.subject_type, run_args.object_type]

    ###########################################################
    ########### RUN TEST SCORES BETWEEN TWO ENTITIES ##########
    ###########################################################
    if run_args.run_option == "test_score":
        run_test_scores(subject = ["heart"], object = ["hypertens"], labels = labels, list_content=list_content, run_args=run_args)
    
    ###########################################################
    ####### RUN CALCULATION SCORES BETWEEN TWO ENTITIES #######
    ###########################################################
    if run_args.run_option == "calculation_score":
        run_calculation_scores(list_content, join_content, entities_path, file_path, labels, run_args)
    ###########################################################
    ################# RUN HYPOTHESIS TEST #####################
    ###########################################################
    if run_args.run_option == "hypothesis_test":
        run_hypothesis_test(file_path, entities_path, labels, run_args)
if __name__ == "__main__":
    main()