from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator


def extract_text_from_pdf(file_name):
    pdf_file_path = f'./data/original_pdf/{file_name}.pdf'
    txt_file_path = f'./data/original_txt/{file_name}.txt'
    
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)



def translate_german_to_english(file_name, chunksize=4500):
    input_file = f'./data/original_txt/{file_name}.txt'
    output_file = f'./data/translated_txt/{file_name}_EN.txt'
    try:
        # translated = GoogleTranslator(source='de', target='en').translate(open(input_file, 'r', encoding='utf-8').read())
        translated_chunks = []

        with open(input_file, 'r', encoding='utf-8') as file:
            for chunk in iter(lambda: file.read(chunksize), ''):
                translated_chunk = GoogleTranslator(source='de', target='en').translate(chunk)
                translated_chunks.append(translated_chunk)

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(''.join(translated_chunks))

    except Exception as e:
        print("Translation Error: ", e)
