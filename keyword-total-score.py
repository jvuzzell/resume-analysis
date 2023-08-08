import csv
import os
import re
from heapq import nlargest
from PyPDF2 import PdfReader

current_directory = os.getcwd()
data_directory = os.path.join(current_directory, "data")
documents_directory = os.path.join(current_directory, "documents")

def read_pdf(file_path): 
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text
    
def parse_pdfs_to_csv(folder_path):
    candidate_urls={}
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file_path.endswith('.pdf'):
            text = read_pdf(file_path)
        else:
            print(f"Skipping unsupported file: {file_path}")
            continue
        candidate_urls[file] = retrieve_urls_from_text(text) 
    return candidate_urls

def extract_urls_from_pdf(pdf_path):
    urls = []
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            annotations = page['/Annots']
            if annotations:
                for annotation in annotations:
                    if annotation['/Subtype'] == '/Link':
                        url = annotation['/A']['/URI']
                        urls.append(url)
    return urls
def retrieve_urls_from_text(text):
    # Use regular expression to find URLs in the extracted text
    return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
def tally_columns(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the header row
        column_totals = {header: 0 for header in headers if header not in ["Section", "Topic", "Keyword"]}
        keywords_by_column = {header: [] for header in headers if header not in ["Section", "Topic", "Keyword"]}

        for row in reader:
            for i, value in enumerate(row[3:]):  # Exclude the first three columns (Section, Topic, and Keyword)
                header = headers[i + 3]
                if header not in ["Section", "Topic", "Keyword"]:
                    column_totals[header] += int(value)
                    keywords_by_column[header].append((int(value), row[2]))  # Use the "Keyword" column value

    return column_totals, keywords_by_column

if __name__ == "__main__":
    csv_file = os.path.join(current_directory, "data/candidate_score_by_section.csv")  # Replace with the actual file path
    column_totals, keywords_by_column = tally_columns(csv_file)

    sorted_column_totals = dict(sorted(column_totals.items(), key=lambda item: item[1], reverse=True))

    candidate_urls = parse_pdfs_to_csv(documents_directory)

    output_file = os.path.join(data_directory, "column_totals_and_keywords.csv")
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File", "Total", "Top 5 Keywords", "URLs"])
        for header, total in sorted_column_totals.items():
            top_5_keywords = nlargest(5, keywords_by_column[header])
            top_5_keywords_str = ', '.join(keyword for _, keyword in top_5_keywords)
            urls = '\n'.join(url for file, urls in candidate_urls.items() for url in urls if file in header)
            writer.writerow([header, total, top_5_keywords_str, urls])

    print("Column totals and top 5 keywords saved to 'column_totals_and_keywords.csv' in the reports directory.")
