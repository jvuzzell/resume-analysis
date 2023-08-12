import os
import json
import PyPDF2
import pandas as pd

current_directory = os.getcwd()

# Function to read the contents of all PDF files in a directory
def read_all_pdf_contents(resumes_directory):
    all_text = {}
    pdf_files = os.listdir(resumes_directory)
    for pdf_file in pdf_files:
        if pdf_file.lower().endswith(".pdf"):
            pdf_path = os.path.join(resumes_directory, pdf_file)
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                all_text[pdf_file] = text
    return all_text

# Function to perform keyword matching on the combined text
def perform_keyword_matching(combined_text, keywords):
    matches = {keyword: combined_text.count(keyword) for keyword in keywords}
    return matches

# Function to process all topics in the JSON and generate the CSV data
def generate_csv_data(json_data, all_text):
    data = []
    pdf_filenames = list(all_text.keys())  # Get the list of PDF filenames
    for section, topics in json_data.items():
        for topic, keywords in topics.items():
            for keyword in keywords:
                row = [section, topic, keyword]
                matches = [0] * len(pdf_filenames)  # Initialize a list with zeros for each PDF
                for i, pdf_file in enumerate(pdf_filenames):
                    pdf_text = all_text.get(pdf_file, "")
                    pdf_matches = perform_keyword_matching(pdf_text, [keyword])
                    matches[i] = pdf_matches.get(keyword, 0)
                row.extend(matches)
                data.append(row)
    return data

# Function to save the CSV data to a file
def save_to_csv(data, output_csv, pdf_filenames):
    df = pd.DataFrame(data, columns=["Section", "Topic", "Keyword"] + pdf_filenames)
    df.to_csv(output_csv, index=False)

# Input JSON and PDF directory 
input_json = os.path.join(current_directory, "keywords/FS_PHP_Dev_001_keywords.json")
resumes_directory = os.path.join(current_directory, "documents/resumes/")  # Replace this with the directory containing your PDF files

# Output CSV
output_csv = os.path.join(current_directory, "data/pg-3_candidate_score_by_section.csv")

# Load the JSON data only once
with open(input_json) as json_file:
    json_data = json.load(json_file)

# Read all PDF contents once
all_text = read_all_pdf_contents(resumes_directory)

# Get the list of PDF filenames
pdf_filenames = list(all_text.keys())

# Generate CSV data and save it to the output CSV file
csv_data = generate_csv_data(json_data, all_text)
save_to_csv(csv_data, output_csv, pdf_filenames)
