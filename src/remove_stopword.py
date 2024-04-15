def remove_stopword(text, nlp):
    doc = nlp(text)
    '''
    for entity in doc.ents:
        print(entity.text, entity.label_)
        print("--------------------------------------")
    '''
    try:
        filtered_txt = [token.text for token in doc if not token.is_stop]
    except:
        print("Error when processing")
    return ' '.join(filtered_txt)
