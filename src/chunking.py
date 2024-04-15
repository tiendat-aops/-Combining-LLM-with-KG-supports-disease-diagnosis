from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import write_to_txt


def get_chunks(file_name, size_chunk, overlap_chunk, text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size_chunk, chunk_overlap=overlap_chunk
    )
    chunks = text_splitter.split_text(text)
    write_to_txt(filename=None, content=None, output_path="output_chunk")
    for i in range(len(chunks)):
        write_to_txt(
            filename=None, content=None, output_path=f"output_chunk/{file_name}"
        )
        name = f"chunk{i}_{size_chunk}character_{file_name}"
        write_to_txt(
            filename=name, content=chunks[i], output_path=f"output_chunk/{file_name}"
        )
