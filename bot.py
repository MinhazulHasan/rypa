from utility.extract_pdf import extract_text_from_pdf, translate_german_to_english
# from services.bot_stream import add_text_to_collection


def main():
    file_name = '1091_11_Ausserbetriebnahme und Entsorgung'
    # extract_text_from_pdf(file_name)
    translate_german_to_english(file_name)
    # add_text_to_collection(file=file_name, word=300)



if __name__ == "__main__":
    main()