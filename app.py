from flask import Flask, render_template, request, send_file
import os
from scrapyy import scrape_search_query  # Your scraping function
from clean import clean_csv_files  # Cleaning function for all files in a folder
from website_scraper import process_csv_files 

app = Flask(__name__, template_folder='model/template')

# Directories for raw and cleaned outputs
RAW_OUTPUT_FOLDER = 'model/output/raw-output'
CLEAN_OUTPUT_FOLDER = 'model/output/clean-output'
SEMI_OUTPUT_FOLDER = 'model/output/semi-output'

# Ensure the directories exist
os.makedirs(RAW_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(CLEAN_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(SEMI_OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query']
        Country = search_query.split()[-1]  

        # Step 1: Scrape and save raw data
        raw_csv_filename = scrape_search_query(search_query, Country)  # Returns the filename, e.g., `{query}.csv`
        raw_file_path = os.path.join(RAW_OUTPUT_FOLDER, raw_csv_filename)
        
        if not os.path.exists(raw_file_path):
            return "Error: Recently scraped file not found.", 500

        # Step 2: Clean all files in raw-output and save them in clean-output
        clean_csv_files(RAW_OUTPUT_FOLDER, CLEAN_OUTPUT_FOLDER)

        # # Step 3: Identify the cleaned file corresponding to the search query
        # cleaned_file_name = raw_csv_filename  # Same name as the raw file
        # cleaned_file_path = os.path.join(CLEAN_OUTPUT_FOLDER, cleaned_file_name)

        # if not os.path.exists(cleaned_file_path):
        #     return f"Error: Cleaned file {cleaned_file_path} not found.", 500
        # Step 3: Scrape additional data from cleaned files and save to semi-output
        process_csv_files()  # This will read from CLEAN_OUTPUT_FOLDER and write to SEMI_OUTPUT_FOLDER

        # Step 4: Identify the semi-cleaned file corresponding to the search query
        semi_cleaned_file_name = raw_csv_filename  # Same name as the raw file
        semi_cleaned_file_path = os.path.join(SEMI_OUTPUT_FOLDER, semi_cleaned_file_name)

        if not os.path.exists(semi_cleaned_file_path):
            return f"Error: Semi-cleaned file {semi_cleaned_file_path} not found.", 500

        # Step 4: Send the cleaned file to the user
        return send_file(semi_cleaned_file_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
