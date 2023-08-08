import docx
import re
import json
import csv
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

def write_individual_scores_to_csv(candidates_scores):
    keywords = set()
    for data in candidates_scores.values():
        keywords.update(data['scores'].keys())

    csv_file = 'individual_scores.csv'
    with open(csv_file, 'w', newline='') as file:
        fieldnames = ['Keyword'] + list(candidates_scores.keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for keyword in keywords:
            row_data = {candidate: data['scores'].get(keyword, 0) for candidate, data in candidates_scores.items()}
            row_data['Keyword'] = keyword
            writer.writerow(row_data)

    print(f"\nIndividual scores have been written to '{csv_file}'.")

def retrieve_urls_from_text(text):
    # Use regular expression to find URLs in the extracted text
    return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

def main(folder_path, current_directory):
    json_file = os.path.join(current_directory, 'keywords', 'FS_PHP_Dev_001_keywords.json')

    keywords_data = load_keywords_from_json(json_file)
    keywords = [keyword for section in keywords_data.values() for keyword_list in section.values() for keyword in keyword_list]

    candidates_scores = {}  # Dictionary to store scores and top 5 categories for each candidate

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
        urls = retrieve_urls_from_text(text)

        # Calculate the total score for the candidate
        total_score = sum(scores.values())

        # Find the top 5 categories and their corresponding scores
        sorted_categories = sorted(scores, key=lambda keyword: scores[keyword], reverse=True)
        top_5_categories = {category: scores[category] for category in sorted_categories[:5]}

        candidates_scores[file] = {'total_score': total_score, 'scores': scores, 'urls': urls, 'top_5_categories': top_5_categories}

    # Sort candidates by total scores in descending order
    sorted_candidates = sorted(candidates_scores.items(), key=lambda item: item[1]['total_score'], reverse=True)

    # Write data to a CSV file
    csv_file = 'candidate_scores.csv'
    with open(csv_file, 'w', newline='') as file:
        fieldnames = ['Candidate', 'Total Score', 'Top Categories', 'URLs']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for candidate, data in sorted_candidates:
            total_score = data['total_score']
            top_categories = ', '.join(data['top_5_categories'].keys())
            urls = ', '.join(data['urls']) if data['urls'] else 'No links'

            writer.writerow({'Candidate': candidate, 'Total Score': total_score, 'Top Categories': top_categories, 'URLs': urls})

    print(f"\nData has been written to '{csv_file}'.")
    
    # Print the sorted candidates from highest to lowest total scores
    print("\nCandidate Scores:")
    for candidate, data in sorted_candidates:
        total_score = data['total_score']
        top_categories = ', '.join(data['top_5_categories'].keys())
        print(f"\n{candidate}:\nTotal Score: {total_score}\nTop Categories: {top_categories}")

        # Print URLs as a list, or "No links" if there are no URLs
        urls = data['urls']
        if urls:
            print("URLs:")
            for url in urls:
                print(f"- {url}")
        else:
            print("- No links")

    write_individual_scores_to_csv(candidates_scores)

if __name__ == "__main__":
    current_directory = os.getcwd()
    print("Current working directory:", current_directory)
    folder_path = os.path.join(current_directory, 'documents')  # Replace with the path to your folder containing Word documents and PDFs
    main(folder_path, current_directory)
