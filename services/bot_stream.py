import os
import json
from PyPDF2 import PdfReader
import re
import queue
from typing import List, Dict
from deep_translator import GoogleTranslator
from chromadb import Client, Settings
from chromadb.utils import embedding_functions
import openai
from dotenv import load_dotenv
load_dotenv()

ef = embedding_functions.ONNXMiniLM_L6_V2()
messages = []
stop_item = "###finish###"
q = queue.Queue()

client = Client(settings = Settings(persist_directory="./client", is_persistent=True))
collection_ = client.get_or_create_collection(name="test", embedding_function=ef)
key = os.environ.get('OPENAI_API_KEY')
openai.api_key = key



def get_text_chunks(text: str, word_limit: int) -> List[str]:
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        words = sentence.split()
        if len(" ".join(current_chunk + words)) <= word_limit:
            current_chunk.extend(words)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = words

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks



def translate_text(text_to_translate):
    translator = GoogleTranslator(source='de', target='en')
    translated_text = translator.translate(text_to_translate)
    return translated_text



def load_pdf(file: str, word: int) -> None:
    file_path = f'./data/original/{file}.pdf'
    reader = PdfReader(file_path)
    documents = {}

    if os.path.exists(f"./client/{file}/documents_en.txt"):
        with open(f"./client/{file}/documents_en.txt", "r", encoding="utf-8") as file:
            documents = json.load(file)
    else:
        for page_no in range(len(reader.pages)):
            page = reader.pages[page_no]
            text = page.extract_text()
            text = translate_text(text)
            text = text.replace('', '')
            text = text.replace('.', '')
            text = text.replace('�', '')
            text_chunks = get_text_chunks(text, word)
            documents[page_no] = text_chunks

        os.makedirs(f'./client/{file}', exist_ok=True)
        with open(f"./client/{file}/documents_en.txt", "w", encoding="utf-8") as file:
            json.dump(documents, file, indent=4)
    
    return documents


def is_subdir_exists(dir_path: str) -> bool:
    for name in os.listdir(dir_path):
        if os.path.isdir(os.path.join(dir_path, name)):
            return True
    return False



def add_text_to_collection(file: str, word: int = 1500) -> None:
    global file_name
    file_name = file
    docs = load_pdf(file, word)

    docs_strings = []
    metadatas = []
    ids = []
    id = 0
    global collection_


    # If docs_strings.txt and metadatas.txt exists, load them
    if os.path.exists(f"./client/{file}/docs_strings.txt") and os.path.exists(f"./client/{file}/metadatas.txt"):
        with open(f"./client/{file}/docs_strings.txt", "r", encoding="utf-8") as f:
            docs_strings = json.load(f)
        with open(f"./client/{file}/metadatas.txt", "r", encoding="utf-8") as f:
            metadatas = json.load(f)
    # Else, create them
    else:
        for page_no in docs.keys():
            for doc in docs[page_no]:
                docs_strings.append(doc)
                metadatas.append({ 'page_no': page_no })
                ids.append(id)
                id += 1
        with open(f"./client/{file}/docs_strings.txt", "w", encoding="utf-8") as f:
            json.dump(docs_strings, f, indent=4)
        with open(f"./client/{file}/metadatas.txt", "w", encoding="utf-8") as f:
            json.dump(metadatas, f, indent=4)
    

    #If persist_directory doesn't exist, create it
    if not is_subdir_exists(f"./client/{file}"):
        client = Client(settings = Settings(persist_directory=f"./client/{file}", is_persistent=True))
        ef = embedding_functions.ONNXMiniLM_L6_V2()
        collection_ = client.get_or_create_collection(name="test", embedding_function=ef)
        collection_.add(
            ids = [str(id) for id in ids],
            documents = docs_strings,
            metadatas = metadatas,
        )
        print("PDF embeddings successfully added to collection")
    # Else, load the collection
    else:
        client = Client(settings = Settings(persist_directory=f"./client/{file}", is_persistent=True))
        ef = embedding_functions.ONNXMiniLM_L6_V2()
        collection_ = client.get_or_create_collection(name="test", embedding_function=ef)
        collection_.get()
        print("PDF embeddings already exist in collection")





def query_collection(text: str, n: int) -> List[str]:
    result = collection_.query(
        query_texts = text,
        n_results = n
    )
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    resulting_strings = []
    for page_no, text_list in zip(metadatas, documents):
        resulting_strings.append(f"{text_list}")
        # resulting_strings.append(f"Page {page_no['page_no']}:{text_list}")
    return resulting_strings
