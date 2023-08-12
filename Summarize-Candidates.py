import csv
import os
import re
from heapq import nlargest
from PyPDF2 import PdfReader

current_directory = os.getcwd()
data_directory = os.path.join(current_directory, "data")
resumes_directory = os.path.join(current_directory, "documents/resumes")

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

def read_parsed_applications(csv_file):
    applications = {}
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            applications[row['Resume File']] = row
    return applications

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
    csv_file = os.path.join(current_directory, "data/pg-3_candidate_score_by_section.csv")
    column_totals, keywords_by_column = tally_columns(csv_file)

    sorted_column_totals = dict(sorted(column_totals.items(), key=lambda item: item[1], reverse=True))

    candidate_urls = parse_pdfs_to_csv(resumes_directory)

    applications = read_parsed_applications(os.path.join(data_directory, "pg-2_parsed_applications.csv"))

# ... [rest of your code]

def read_parsed_applications(csv_file):
    applications = {}
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            applications[row['Resume File']] = row
    return applications

if __name__ == "__main__":
    # ... [rest of your code]

    applications = read_parsed_applications(os.path.join(data_directory, "pg-2_parsed_applications.csv"))

    output_file = os.path.join(data_directory, "pg-1_column_totals_and_keywords.csv")
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Reordering the columns
        writer.writerow(["Job Title", "First Name", "Last Name", "Email", "Cell Phone", "Resume", "Keyword Match Total", "Top 10 Keywords", "URLs", "Application Date", "Available Start Date", "Desired Compensation", "Country", "State", "City", "Zip/Postal Code", "Are you 18 years of age or older?", "Are you legally authorized to work in the United States?", "How did you hear about this opportunity?"])
        
        for header, total in sorted_column_totals.items():
            top_keywords = nlargest(10, keywords_by_column[header])
            top_keywords_str = ', '.join(keyword for _, keyword in top_keywords)
            urls = ', \n'.join(url for file, urls in candidate_urls.items() for url in urls if file in header)
            
            application = applications.get(header, {})
            application_data = [
                application.get(column, "") for column in ["Job Title", "First Name", "Last Name", "Email", "Cell Phone", "Application Date", "Available Start Date", "Desired Compensation", "Country", "State", "City", "Zip/Postal Code", "Are you 18 years of age or older?", "Are you legally authorized to work in the United States?", "How did you hear about this opportunity?"]
            ]

            # Reordering the row data
            writer.writerow(application_data[:5] + [header, total, top_keywords_str, urls] + application_data[5:])

    print("Column totals, top 5 keywords, and application data saved to 'column_totals_and_keywords.csv' in the data directory.")

