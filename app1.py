from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import csv
from model.main.scrapyy import scrape_search_query  
from model.main.clean import clean_csv_files 
from model.main.visit import process_csv_files 
from model.main.remove import clean_and_save_csv 
from model.main.follower import fetch_followers ,save_to_csv

# from model.main.instadetail import fetch_user_details, read_usernames_from_csv

app = Flask(__name__, template_folder='model/template')

RAW_OUTPUT_FOLDER = 'model/output/raw-output'
CLEAN_OUTPUT_FOLDER = 'model/output/clean-output'
SEMI_OUTPUT_FOLDER = 'model/output/semi-output'
FINAL_OUTPUT_FOLDER = 'model/output/final-output'

os.makedirs(RAW_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(CLEAN_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(SEMI_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(FINAL_OUTPUT_FOLDER, exist_ok=True)

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
    file_path = os.path.join(FINAL_OUTPUT_FOLDER, filename)
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
            # Step 1: Scrape raw data
            print(f"Scraping data for query: {search_query}")
            csv_filename = scrape_search_query(search_query, Country)
            print(f"csv_filename: {csv_filename}")
            raw_file_path = os.path.join(RAW_OUTPUT_FOLDER, csv_filename)
            
            if not os.path.exists(raw_file_path,):
                return f"Error: Scraped file {csv_filename} not found in {RAW_OUTPUT_FOLDER}.", 500

            # Step 2: Clean raw data
            print(f"Cleaning raw data: {csv_filename}")
            clean_csv_files(RAW_OUTPUT_FOLDER, CLEAN_OUTPUT_FOLDER, csv_filename)

            #Step 3: Process cleaned data to extract additional details
            print(f"Processing cleaned data: {csv_filename}")
            clean_file_path = os.path.join(CLEAN_OUTPUT_FOLDER, csv_filename)
            if not os.path.exists(clean_file_path):
                return f"Error: Cleaned file {csv_filename} not found in {CLEAN_OUTPUT_FOLDER}.", 500
            
            # Step 3: Process cleaned data
            process_csv_files()

            # Step 4: Process semi-cleaned data
            print(f"Processing semi-cleaned data: {csv_filename}")
            processed_filename = os.path.join(SEMI_OUTPUT_FOLDER, csv_filename)
             
            # Check if processed file was created
            if not processed_filename:
                return "Error: Processed file not found after processing.", 500
            
            #step5 :clean and save data
            print(f"Cleaning and saving data: {csv_filename}")
            clean_and_save_csv(SEMI_OUTPUT_FOLDER, FINAL_OUTPUT_FOLDER, csv_filename)

            final_csv_filename = os.path.join(FINAL_OUTPUT_FOLDER, csv_filename)
            if not os.path.exists(final_csv_filename):
                return "Error: Final CSV not found.", 500
            
            csv_data = []
            with open(final_csv_filename, newline='', encoding='utf-8') as csvfile:
                csvreader = csv.reader(csvfile)
                headers = next(csvreader)  
                for row in csvreader:
                    csv_data.append(row)
            return render_template('business.html', scraped_file=f"{csv_filename}", final_csv_filename=final_csv_filename,csv_data=csv_data)

        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    return render_template('business.html')


# @app.route('/instagram', methods=['GET', 'POST'])
# def instagram_scraping():
#     if request.method == 'POST':
#         username = request.form['username']
        
#         try:
#             # Step 1: Fetch followers
#             print(f"Fetching followers for username: {username}")
#             followers_output_file = os.path.join(RAW_OUTPUT_FOLDER, f"{username}_followers.csv")
#             fetch_followers(username, followers_output_file)
            
#             if not os.path.exists(followers_output_file):
#                 return f"Error: Followers file {followers_output_file} not found.", 500

            # # Step 2: Read followers' usernames from CSV
            # print("Reading followers' usernames from CSV...")
            # followers_usernames = read_usernames_from_csv(followers_output_file)

            # # Step 3: Fetch user details for each follower
            # print("Fetching user details...")
            # user_details_output_file = os.path.join(CLEAN_OUTPUT_FOLDER, f"{username}_user_details.csv")
            # fetch_user_details(followers_usernames, user_details_output_file)

            # if not os.path.exists(user_details_output_file):
            #     return f"Error: User details file {user_details_output_file} not found.", 500

    #         return render_template('instagram.html', scraped_file=f"{username}_user_details.csv")
        
    #     except Exception as e:
    #         print(f"Error during Instagram scraping: {str(e)}")
    #         return f"An error occurred: {str(e)}", 500

    # return render_template('instagram.html')




@app.route('/instagram', methods=['GET', 'POST'])
def instagram_scraping():
    if request.method == 'POST':
        username = request.form['username']  

        try:
    
            print(f"Fetching followers for username: {username}")
            followers_output_file = os.path.join(RAW_OUTPUT_FOLDER, f"{username}_followers.csv")
            
      
            followers = fetch_followers(username) 
            
            save_to_csv(followers, followers_output_file)  
            
            if not os.path.exists(followers_output_file):
                return f"Error: Followers file {followers_output_file} not found.", 500

            return render_template('instagram.html', scraped_file=f"{username}_followers.csv")

        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error occurred while processing: {e}", 500

    return render_template('instagram.html') 

if __name__ == '__main__':
    app.run(debug=True)
