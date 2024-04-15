import nltk
from nltk.tokenize import RegexpTokenizer, word_tokenize
import string
from nltk.stem import WordNetLemmatizer,PorterStemmer
from nltk.corpus import stopwords
import re
import pandas as pd
# import spacy

# nlp = spacy.load("en_core_web_lg")
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer() 
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

entities_path = "/work/dat-nt/LLM/code/src/data_processing/keyword/entities_final.csv"
special_characters = ['!','@', '—', '#','$','%','^','&','*','(',')','-','_','+','=','{','}','[',']','|','\\',';',':',"'",'"',',','/','<','>','?','~','`', '•', "“", "”", "’"]

def preprocess(sentence, option = 'nltk'):
    sentence=str(sentence)
    sentence = sentence.lower()
    sentence=sentence.replace('{html}',"") 
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', sentence)
    rem_url=re.sub(r'http\S+', '',cleantext)
    rem_num = re.sub('[0-9]+', '', rem_url)
    if option == 'nltk':
        tokenizer = RegexpTokenizer(r'\s+', gaps="True")
        tokens = tokenizer.tokenize(rem_num)  
        filtered_words = [w for w in tokens if not w in stopwords.words('english')]
        stem_words=[stemmer.stem(w) for w in filtered_words]
        lemma_words=[lemmatizer.lemmatize(w) for w in stem_words]
    elif option == 'spacy':
        pass
        # doc = nlp(rem_num)
    # print(lemma_words)
    res = []
    for word in lemma_words:
        new_word = ""
        word = word.replace("-", "")
        for char in word:
            if char not in special_characters:
                new_word += char
            else: new_word += ' '
        if new_word == 'e.g.': continue
        if new_word == '.': res.append(new_word)
        if len(new_word) > 3:
            res.append(new_word)
    return ' '.join(res).strip()

def preprocess_keyword(entities_path = entities_path, label = 'all'):
    entity_frame = pd.read_csv(entities_path)
    entity_list = entity_frame['name'].tolist()
    entity_frame["name_processed"] = entity_frame['name'].apply(lambda x: preprocess(x))
    entity_frame.to_csv(entities_path)

def load_entity(entities_path = entities_path, label = 'all'):
    entity_frame = pd.read_csv(entities_path)
    entity_list = entity_frame['name'].tolist()
    label_entity = entity_frame['label'].tolist()
    #print(len(entity_list))
    entity_processed = []
    try:
        for entity in entity_list:
            new_entity = preprocess(entity)
            entity_processed.append(new_entity)
    except: print("Error when processing entities")
    if label == 'all':
        key_entity = {key : 0 for key in entity_processed}
    else:
        entity_label = [entity for i, entity in enumerate(entity_processed) if label_entity[i] == label]
        key_entity = {key : 0 for i, key in enumerate(entity_processed) if label_entity[i] == label}
        return key_entity, entity_label
    return key_entity, entity_processed


def count_keyword(file_content = '', key_entity = {}, entity = [], number_occur = 10):
    # word_list = file_content.split()
    words = word_tokenize(file_content)
    word_list = [word for word in words if word not in string.punctuation]
    for word in word_list:
        word = word.strip()
        if word in entity:
            key_entity[word] += 1
    keys_to_remove = [key for key, value in key_entity.items() if value < number_occur]
    for key in keys_to_remove:
        del key_entity[key]
    return key_entity

def create_dict_name_mean(entities_path = entities_path, label = 'all'):
    # dict_name_mean = {}
    df = pd.read_csv(entities_path)
    name = df.name.tolist()
    name_vi = df.name_vi.tolist()
    dict_name_mean = {name[i]:name_vi[i] for i in range(len(name))}
    return dict_name_mean
    
def create_dict_name_processed_name(entities_path = entities_path, label = 'all'):
    df = pd.read_csv(entities_path)
    name_processed = df.name_processed.tolist()
    name = df.name.tolist()
    dict_name_processed_name = {name_processed[i]:name[i] for i in range(len(name))}
    return dict_name_processed_name

def convert_list_content_to_list_word(list_content):
    list_words = []
    for content in list_content: 
        words = word_tokenize(content)
        word_lists = [word for word in words if word not in string.punctuation]
        list_words.append(word_lists)
    return list_words
# print(create_dict_name_processed_name())
# preprocess_keyword()
#key_entity, entity = load_entity(label='organ')
#print(key_entity)
# print(preprocess("thrombocyto-penia"))
#file_content = "Hello I am Tien Dat"
#print(count_keyword(file_content = file_content, key_entity=key_entity, entity = entity))
#text = "The weather (today) is cloudy."
#print(preprocess(text))
