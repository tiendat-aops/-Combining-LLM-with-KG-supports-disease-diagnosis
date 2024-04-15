import math
from split_content import sentence_split
from nltk.tokenize import word_tokenize
import numpy as np

def laplacian_func(x, alpha):
    # print("x value: ", x)
    return math.exp(-alpha*x)

def laplacian_func_tf(x, tf, alpha):
    beta = alpha + math.exp(tf)
    # print("beta_value : ", beta)
    return math.exp(-beta*x)

def softmax(x):
    e_x = np.exp(x - np.max(x))  # Subtracting the maximum value for numerical stability
    return e_x / e_x.sum()

def find_all_indexes(sentence, word):
    indexes = []
    index = -1
    while True:
        index = sentence.find(word, index + 1)
        if index == -1:
            break
        if sentence[index-1] == ' ' and index + len(word) == len(sentence):
            indexes.append(index)
        elif sentence[index-1] == ' ' and sentence[index + len(word)] == ' ':
            indexes.append(index)
        elif index == 0 and sentence[index + len(word)] == ' ':
            indexes.append(index)
        elif sentence[index + len(word)] == '.':
                indexes.append(index)
    return indexes

def cal_interaction_value(subject, object, sent_list, alpha, tf = 0, func_option = "org"):
    #sent_list = sentence_split(file_content)
    dict_object = {subject: 0, object: 1}
    list_index_subject = []
    list_index_object = []
    for sent in sent_list:
        indexes_subject = find_all_indexes(sent, subject)
        list_index_subject += [indexes_subject]
        indexes_object = find_all_indexes(sent, object)
        list_index_object += [indexes_object]
    list_index = []
    index_sent = []
    index_word = []
    for i in range(len(list_index_subject)):
        index_subject = list_index_subject[i]
        index_object = list_index_object[i]
        index = index_subject + index_object
        
        index.sort()
    
        try:
            for idx in index:
                if idx in index_subject:
                    index_word.append(dict_object[subject])
                    index_sent.append(i)
                else:
                    index_word.append(dict_object[object])
                    index_sent.append(i)
        except: 
            continue

    check = False
    first_index_subject = 0
    first_index_object = 0
    check = False
    for i, word in enumerate(index_word):
        if word == dict_object[subject]:
            first_index_subject = i
            check = True
            break

    score = 0
    for i, word in enumerate(index_word):
        if i < first_index_subject:
            continue
        if word == dict_object[subject]:
            first_index_subject = i
        elif word == dict_object[object]:
            if check:
                x = index_sent[i] - index_sent[first_index_subject]
                if func_option == "org":
                    score += laplacian_func(x, alpha)
                else:
                    score += laplacian_func_tf(x, tf, alpha)
    return score

# print(laplacian_func_tf(x = 2, tf = 1, alpha=1))
# print(laplacian_func(x=2, alpha=1))
# import time
# # Test calculation score
# start = time.time()
# #“AAAB.BAABB.ABB”
# text = ["A A A B.", "B A A B B.", "A B B"]

# subject = "B"
# object = "A"
# # print(text[0][65+len(object)])
# print(cal_interaction_value(subject, object, text, 1))
# end = time.time()
# print(end - start)