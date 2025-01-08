from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from model.main.scrapy import scrape_search_query  
from model.main.clean import clean_csv_files 
from model.main.visit import process_csv_files
from model.main.follower import fetch_followers_with_pagination 
from model.main.instadetail import fetch_user_details, read_usernames_from_csv

app = Flask(__name__, template_folder='model/template')

RAW_OUTPUT_FOLDER = 'model/output/raw-output'
CLEAN_OUTPUT_FOLDER = 'model/output/clean-output'
SEMI_OUTPUT_FOLDER = 'model/output/semi-output'

os.makedirs(RAW_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(CLEAN_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(SEMI_OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        scraping_type = request.form['scraping_type']
        
        if scraping_type == 'business':
            return redirect(url_for('business_scraping'))
        elif scraping_type == 'instagram':
            return redirect(url_for('instagram_scraping'))
            
    return render_template('index.html')

@app.route('/download/business/<filename>')
def download_business(filename):
    file_path = os.path.join(SEMI_OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Error: File not found.", 404

@app.route('/download/instagram/<filename>')
def download_instagram(filename):
    file_path = os.path.join(CLEAN_OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Error: File not found.", 404

@app.route('/business', methods=['GET', 'POST'])
def business_scraping():
    if request.method == 'POST':
        search_query = request.form['search_query']
        Country = search_query.split()[-1] 

        try:
            # Step 1: Scrape and save raw data
            raw_csv_filename = scrape_search_query(search_query, Country) 
            raw_file_path = os.path.join(RAW_OUTPUT_FOLDER, raw_csv_filename)  

            print(f"Raw file path: {raw_file_path}")
            if not os.path.exists(raw_file_path):
                return f"Error: Scraped file {raw_file_path} not found.", 500

            # Step 2: Clean raw data
            print("Starting to clean raw data...")
            clean_csv_files(RAW_OUTPUT_FOLDER, CLEAN_OUTPUT_FOLDER) 
            print(f"Cleaned CSV files from {RAW_OUTPUT_FOLDER} to {CLEAN_OUTPUT_FOLDER}")

            # Step 3: Process cleaned data
            process_csv_files()  
            print(f"Processed CSV files saved in {SEMI_OUTPUT_FOLDER}")

            semi_cleaned_file_name = raw_csv_filename  
            semi_cleaned_file_path = os.path.join(SEMI_OUTPUT_FOLDER, semi_cleaned_file_name)
            
            if not os.path.exists(semi_cleaned_file_path):
                return f"Error: Semi-cleaned file {semi_cleaned_file_path} not found.", 500

            return render_template('business.html', scraped_file=semi_cleaned_file_name)

        except Exception as e:
            print(f"Error during processing: {str(e)}")
            return f"An error occurred: {str(e)}", 500

    return render_template('business.html')

# Instagram scraping route
@app.route('/instagram', methods=['GET', 'POST'])
def instagram_scraping():
    if request.method == 'POST':
        username = request.form['username']
        
        try:
            # Step 1: Fetch followers data
            followers_output_file = os.path.join(RAW_OUTPUT_FOLDER, f"{username}_followers.csv")
            fetch_followers_with_pagination(username, followers_output_file)  
            
            # Step 2: Read the followers' usernames from the CSV
            followers_usernames = read_usernames_from_csv(followers_output_file)
            
            # Step 3: Fetch user details for each follower
            user_details_output_file = os.path.join(CLEAN_OUTPUT_FOLDER, f"{username}_user_details.csv")
            fetch_user_details(followers_usernames, user_details_output_file)  # Pass the list of usernames
            
            return render_template('instagram.html', scraped_file=f"{username}_user_details.csv")
        
        except Exception as e:
            print(f"Error during Instagram scraping: {str(e)}")
            return f"An error occurred: {str(e)}", 500

    return render_template('instagram.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
