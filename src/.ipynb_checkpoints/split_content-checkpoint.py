import os
from utils import write_to_txt
from pdf_file import PdfFile
from chunking import get_chunks
import spacy
from tqdm import tqdm
from preprocess import preprocess
import nltk
from nltk.tokenize import sent_tokenize
import random
nltk.download('punkt')

def sentence_split(file_content):
    return [s for s in sent_tokenize(file_content)]

def split_list_by_len(lst, avg_len):
    """Split a list into sublists with approximately equal average lengths."""
    n = len(lst)
    start = 0
    for i in range(avg_len):
        end = start + (n - start) // (avg_len - i)
        yield lst[start:end]
        start = end

def split_list_by_n_chunk(lst, n):
    """Split a list into n equal-sized sublists."""
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def chunk_content(content, n_chunk = 50, output_dir = ''):

    content = content.strip()
    sent_list = sentence_split(content)

    split_lists = split_list_by_n_chunk(sent_list, n_chunk)
    print(len(split_lists))
    list_content = [' '.join(x).strip() for x in split_lists]
    return split_lists, list_content


def get_all_content(data_dir, output_dir, output_name):
    file_names = os.listdir(data_dir)
    f = open(f"{output_dir}/{output_name}", 'a')
    list_content = []
    for file_name in tqdm(file_names):
        print(f"Start processing file {file_name}")
        # load file path
        file_dir = os.path.join(data_dir, file_name)
        file_name = file_name.replace(".pdf", "")
        
        # load file and process data
        file = PdfFile(file_path=file_dir)
        file_content = file.get_content()

        try:
            filtered_text = preprocess(file_content)
        except:
            print(f"Error when preprocessing file {file_name}")
        print(f"doneeeee {file_name}")
        list_content.append(filtered_text)
    random.shuffle(list_content)
    f.write('\n'.join(list_content))

def get_all_content_by_pages(data_dir, output_dir, output_name):
    file_names = os.listdir(data_dir)
    f = open(f"{output_dir}/{output_name}", 'a')
    list_content = []
    for file_name in tqdm(file_names):
        if file_name == ".ipynb_checkpoints": continue
        print(f"Start processing file {file_name}")
        # load file path
        file_dir = os.path.join(data_dir, file_name)
        file_name = file_name.replace(".pdf", "")
        
        # load file and process data
        file = PdfFile(file_path=file_dir)
        chapters_page = file.get_content_by_chapters_page()
        for chapter in chapters_page:
            for page in chapter["content"]:
                if page['content'] != '': 
                    try:
                        filtered_text = preprocess(page['content'])
                    except:
                        print(f"Error when preprocessing file {file_name}")
                    list_content.append(filtered_text)
    random.shuffle(list_content)
    f.write('\n'.join(list_content))
            
        
### TEST FUNCTION
#content = "For example, a system can. generate 100 tokens per second. If the system generates 1000 tokens, with the non-streaming setup, users need to wait 10 seconds to. get results. On the other hand, with the streaming setup, users get initial results immediately, and although end-to-end. latency will be the same, they can see half of the generation. after five seconds."
#print(chunk_content(content, n_chunk=3))
