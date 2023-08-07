import docx
import re
import json
from PyPDF2 import PdfReader
import os

def read_word_document(file_path):
    doc = docx.Document(file_path)
    text = ' '.join([para.text for para in doc.paragraphs])
    return text

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def keyword_match(text, keywords):
    scores = {keyword: 0 for keyword in keywords}

    for keyword in keywords:
        occurrences = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
        scores[keyword] += occurrences

    return scores

def load_keywords_from_json(json_file):
    with open( json_file, 'r') as file:
        keywords_data = json.load(file)
    return keywords_data

def main(folder_path, current_directory):
    json_file = current_directory + '/keywords/FS_PHP_Dev_001_keywords.json'


    keywords_data = load_keywords_from_json(json_file)
    keywords = [keyword for section in keywords_data.values() for keyword_list in section.values() for keyword in keyword_list]

    candidates_scores = {}  # Dictionary to store scores for each candidate

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if file_path.endswith('.docx'):
            text = read_word_document(file_path)
        elif file_path.endswith('.pdf'):
            text = read_pdf(file_path)
        else:
            print(f"Skipping unsupported file: {file_path}")
            continue

        scores = keyword_match(text, keywords)

        # Calculate the total score for the candidate
        total_score = sum(scores.values())
        candidates_scores[file] = {'total_score': total_score, 'scores': scores}

    # Calculate the top 5 categories for each candidate
    top_5_categories_per_candidate = {}

    for candidate, data in candidates_scores.items():
        scores = data['scores']
        sorted_categories = sorted(scores, key=lambda keyword: scores[keyword], reverse=True)
        top_5_categories = sorted_categories[:5]
        top_5_categories_per_candidate[candidate] = {'total_score': data['total_score'], 'top_categories': top_5_categories}

    # Print the total score and top 5 categories for each candidate
    print("\nCandidate Scores:")
    for candidate, data in top_5_categories_per_candidate.items():
        total_score = data['total_score']
        top_categories = ', '.join(data['top_categories'])
        print(f"{candidate}: \n  -Total Score: {total_score}, \n  -Top Categories: {top_categories}\n\n")

if __name__ == "__main__": 
    current_directory = os.getcwd()
    print("Current working directory:", current_directory)
    folder_path = current_directory + '/documents'  # Replace with the path to your folder containing Word documents and PDFs
    main(folder_path, current_directory)
