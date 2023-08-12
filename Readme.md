# Resume Analysis

Welcome to the Resume Analysis tool documentation. This project automates the process of extracting relevant information from resumes, processing it, and generating concise reports for quicker review.

## Table of Contents
1. [Getting Started](#getting-started)
2. [File Structure](#file-structure)
3. [Functionalities](#functionalities)
4. [Usage Guide](#usage-guide)
5. [Contribute](#contribute)
6. [License](#license)

## Getting Started

### Prerequisites

- Python 3.x
- Pip (Python package installer)

### Installation

Clone the repository:
```bash
git clone https://github.com/your-username/resume-analysis.git
``` 

Navigate to the project directory: 
```bash
cd resume-analysis
```

Install the required packages: 
```bash
pip install -r requirements.txt
``` 

### How to Use
1. **Setup:** 
    - Ensure that all resumes are saved as PDFs in the documents/resumes directory.
    - Make sure the keywords/FS_PHP_Dev_001_keywords.json file contains the list of keywords to be matched against.
2. **Keyword Matching:**
    - Run Keyword-Match-Resume.py to perform keyword matching on all resumes and save the result as a CSV.
3. **Summarizing Candidates:**
    - Execute Summarize-Candidates.py to summarize candidate details, extract URLs, and consolidate keyword matching results.
4. **Generating Excel Report:**
    - Run Create-Excel-Book.py to create an Excel workbook where each CSV report is saved as a separate sheet.
    - Check the generated Excel file under reports/resume_review.xlsx for the results.

## File Structure 
```
.
├── documents
│   └── resumes      # Contains the PDF resumes to be processed
├── data             # Directory for CSV and other 
├── keywords         # JSON files containing keywords 
├── reports
│   └── resume_review.xlsx   # Final Excel report
├── Keyword-Match-Resume.py  # Script for keyword matching
├── Summarize-Candidates.py  # Script to process and summarize data
├── Create-Excel-Book.py     # Script to consolidate CSVs into an Excel file
└── requirements.txt         # Required Python packages

```
 
## License 

This project is licensed under the MIT License. See the LICENSE.md file for details.
