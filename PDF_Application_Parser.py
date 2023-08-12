import re
import csv
import os
from PyPDF2 import PdfReader, PdfFileReader

# Define patterns for sections and their values
PATTERNS = {
        "Application Date": r"Application Date:\s*(?P<ApplicationDate>[\d/]+)",
        "Job Title": r"Job Title:\s*(?P<JobTitle>[^\n]+)",
        "First Name": r"First Name:\s*(?P<FirstName>\w+)",
        "Last Name": r"Last Name:\s*(?P<LastName>\w+)",
        "Email": r"Email:\s*(?P<Email>[\w.@]+)",
        "Country": r"Country:\s*(?P<Country>\w+)",
        "State": r"State:\s*(?P<State>\w+)",
        "City": r"City:\s*(?P<City>\w+)",
        "Zip/Postal Code": r"Zip/Postal Code:\s*(?P<ZipCode>[\d\s]+)",
        "Cell Phone": r"Cell Phone:\s*(?P<CellPhone>[\d\s]+)",
        "Are you 18 years of age or older?": r"Are you 18 years of age or older\?\s*(?P<Age18>\w+)",
        "Are you legally authorized to work in the United States?": r"Are you legally authorized to work in the United States\?\s*(?P<AuthorizedToWork>\w+)",
        "Desired Compensation": r"Desired Compensation:\s*(?P<DesiredCompensation>[,\d\-\.]+(\s*/\s*hr)?)",
        "Available Start Date": r"Available Start Date:\s*(?P<StartDate>[\d/]+)",
        "How did you hear about this opportunity?": r"How did you hear about this opportunity\?\s*(?P<OpportunitySource>\w+)"
        # Add more patterns as needed
    }

current_directory = os.getcwd()
data_directory = os.path.join(current_directory, "data")
applications_directory = os.path.join(current_directory, "documents/applications")
resumes_directory = os.path.join(current_directory, "documents/resumes")

def read_pdf(file_path): 
    text_pages = []
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text_pages.append(page.extract_text())
        return ''.join(text_pages)
    except (PdfFileReader.PdfReadError, KeyError):
        print(f"Error reading file: {file_path}")
        return None

def parse_application_text(text):
    parsed_data = {}
    for key, pattern in PATTERNS.items():
        match = re.search(pattern, text)
        if match:
            parsed_data[key] = match.group(match.lastgroup)
    return parsed_data

def parse_application(folder_path):  
    application_meta = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.pdf'):
                text = read_pdf(file_path)
                if text is not None:
                    parsed_data = parse_application_text(text)
                    if parsed_data:
                        application_meta[file] = parsed_data
            else:
                print(f"Skipping unsupported file: {file_path}")
    return application_meta

def match_pdf_with_data(directory, parsed_applications):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.pdf'):
                text = read_pdf(file_path)
                if text:
                    for app_file, app_data in parsed_applications.items():
                        first_name_pattern = re.compile(re.escape(app_data.get('First Name')), re.IGNORECASE)
                        last_name_pattern = re.compile(re.escape(app_data.get('Last Name')), re.IGNORECASE)

                        if first_name_pattern.search(text) and last_name_pattern.search(text):
                            parsed_applications[app_file]["Resume File"] = file  # add a "Document Match" entry to the application data
                            break  # break once a match is found for a PDF

    return parsed_applications

if __name__ == "__main__":
    applications = parse_application(applications_directory) 
    
    applications = match_pdf_with_data(resumes_directory, applications)

    output_file = os.path.join(data_directory, "pg-2_parsed_applications.csv")
    with open(output_file, 'w', newline='') as csvfile:
        # CSV Header using the keys from PATTERNS, prefixed by 'Filename'
        fieldnames = ['Application'] + list(PATTERNS.keys()) + ['Resume File']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for file_name, parsed_data in applications.items():
            # Write file_name followed by parsed data to CSV
            writer.writerow({'Application': file_name, **parsed_data})