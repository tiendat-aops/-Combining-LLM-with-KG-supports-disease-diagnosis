import math      

def term_frequency(entity, words):
    result = 0
    for word in words:
        if word == entity:
            result += 1
    return result/len(words)

def invert_document_frequency(entity, docs):
    result = 0
    for doc in docs:
        if word in doc:
            result +=1 
            break
    if result == 0:
        return result
    return math.log(len(docs)/ result, math.e)

def tf_idf(entity, words, docs):
    return term_frequency(entity, words) * invert_document_frequency(entity, docs)

