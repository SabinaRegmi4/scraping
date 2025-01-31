from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import csv
from flask import request, render_template
from scrapyy import scrape_search_query  
from model.main.clean import clean_csv_files 
from model.main.visit import process_csv_files 
from model.main.remove import clean_and_save_csv 
from model.main.follower import fetch_followers, save_to_csv
from model.main.instadetail import process_usernames_from_csv
from model.main.tech import fetch_data,save_to_csv 


app = Flask(__name__, template_folder='model/template')

RAW_OUTPUT_FOLDER = 'model/output/raw-output'
CLEAN_OUTPUT_FOLDER = 'model/output/clean-output'
SEMI_OUTPUT_FOLDER = 'model/output/semi-output'
FINAL_OUTPUT_FOLDER = 'model/output/final-output'
OUTPUT_FOLDER ='model/insta'
FINAL_FOLDER = 'model/insta/output'

os.makedirs(RAW_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(CLEAN_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(SEMI_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(FINAL_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(FINAL_FOLDER, exist_ok=True)

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

@app.route('/business', methods=['GET', 'POST'])
def business_scraping():
    if request.method == 'POST':
        search_query = request.form['search_query']
        country = search_query.split()[-1]  # Get the country name
        
        try:
            # Step 1: Scrape raw data
            print(f"Scraping data for query: {search_query}")
            filename = f"health_industry_in_{country.lower()}.csv"  # Consistent filename
            
            # Scrape and save raw data
            success = scrape_search_query(search_query, country)
            if not success:
                return "Error: Failed to scrape data", 500
            
            # Define all file paths
            raw_file_path = os.path.join(RAW_OUTPUT_FOLDER, filename)
            clean_file_path = os.path.join(CLEAN_OUTPUT_FOLDER, filename)
            semi_file_path = os.path.join(SEMI_OUTPUT_FOLDER, filename)
            final_file_path = os.path.join(FINAL_OUTPUT_FOLDER, filename)
            
            # Check if raw file exists
            if not os.path.exists(raw_file_path):
                return f"Error: Scraped file not found at {raw_file_path}", 500
            
            # Step 2: Clean raw data
            print("Cleaning raw data...")
            clean_csv_files(RAW_OUTPUT_FOLDER, CLEAN_OUTPUT_FOLDER, filename)
            
            if not os.path.exists(clean_file_path):
                return f"Error: Cleaned file not found at {clean_file_path}", 500
            
            # Step 3: Process cleaned data
            print("Processing cleaned data...")
            process_csv_files()
            
            if not os.path.exists(semi_file_path):
                return f"Error: Semi-processed file not found at {semi_file_path}", 500
            
            # Step 4: Final cleaning and saving
            print("Performing final cleaning...")
            clean_and_save_csv(SEMI_OUTPUT_FOLDER, FINAL_OUTPUT_FOLDER, filename)
            
            if not os.path.exists(final_file_path):
                return f"Error: Final file not found at {final_file_path}", 500
            
            return render_template('business.html', scraped_file=filename)
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")  
            return f"An error occurred: {str(e)}", 500
            
    return render_template('business.html')

# app.route('/download/instagram/<filename>')
# def download_instagram(filename):
#     try:
        
#         file_path = os.path.abspath(os.path.join(OUTPUT_FOLDER, filename))
     
#         if not file_path.startswith(os.path.abspath(OUTPUT_FOLDER)):
#             return "Invalid file path", 400
            
#         if os.path.exists(file_path):
#             return send_file(
#                 file_path,
#                 as_attachment=True,
#                 download_name=filename 
#             )
#         else:
#             return "Error: File not found.", 404
#     except Exception as e:
#         print(f"Download error: {str(e)}")
#         return "Error during download", 500

# @app.route('/instagram', methods=['GET', 'POST'])
# def instagram_scraping():
#     error_message = None
#     success_message = None
#     scraped_file = None
    
#     if request.method == 'POST':
#         username = request.form['username']
        
#         try:
#             print(f"Fetching followers for username: {username}")
#             followers = fetch_followers(username)
            
#             if not followers:
#                 error_message = f"No followers fetched for {username}."
#                 return render_template('instagram.html', 
#                                     error_message=error_message)
            
#             os.makedirs(OUTPUT_FOLDER, exist_ok=True)

#             followers_output_file = f"{username}_followers.csv"
#             csv_file_path = os.path.join(OUTPUT_FOLDER, followers_output_file)
 
#             save_to_csv(followers, csv_file_path)
#             print(f"Followers saved to: {csv_file_path}")

#             success_message = "Data scraped successfully!"
#             scraped_file = followers_output_file
            
#             return render_template('instagram.html',
#                                  success_message=success_message,
#                                  scraped_file=scraped_file)
            
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             error_message = f"An error occurred: {str(e)}"
#             return render_template('instagram.html', 
#                                  error_message=error_message)
    

#     return render_template('instagram.html')

@app.route('/download/instagram/<filename>')
def download_instagram(filename):
    file_path = os.path.join("model/insta", filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Error: File not found.", 404

@app.route('/instagram', methods=['GET', 'POST'])
def instagram_scraping():
    if request.method == 'POST':
        username = request.form['username']  

        try:
            print(f"Fetching followers for username: {username}")
            followers = fetch_followers(username)

            if not followers:
                return f"No followers fetched for {username}.", 500
            
            if not os.path.exists(OUTPUT_FOLDER):
                os.makedirs(OUTPUT_FOLDER)
            
            followers_output_file = f"{username}_followers.csv"
            csv_file_path = os.path.join(OUTPUT_FOLDER, followers_output_file)
            save_to_csv(followers, csv_file_path)

            print(f"Followers saved to: {csv_file_path}") 
            scraped_file = followers_output_file
            return render_template('instagram.html', scraped_file=followers_output_file)

        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error occurred while processing: {e}", 500

    return render_template('instagram.html')


@app.route('/search', methods=['GET', 'POST'])
def instagram_tech_scraping():
    if request.method == 'POST':
        search_query = request.form['search_query']
        print(f"Search query received: {search_query}")

        filename = f"{FINAL_FOLDER}/{search_query.replace(' ', '_')}.csv"
        data = fetch_data(search_query)

        print("Fetched Data:", data)

        if data and "data" in data and "items" in data["data"]:
            rows = [
                {
                    "Username": entry.get("username", ""),
                    "Full Name": entry.get("full_name", ""),
                    "Email": entry.get("email", ""),
                    "Phone": entry.get("phone", ""),
                    "Website": entry.get("website", ""),
                    "Followers": entry.get("followers", ""),
                    "Following": entry.get("following", ""),
                    "Biography": entry.get("biography", ""),
                    "Profile Picture URL": entry.get("profile_picture_url", "")
                }
                for entry in data["data"]["items"]
                if isinstance(entry, dict)
            ]

            if rows:
                print(f"Rows to save: {rows}") 
                with open(filename, mode='w', newline='', encoding='utf-8') as file:
                    fieldnames = ["Username", "Full Name", "Email", "Phone", "Website", "Followers", "Following", "Biography", "Profile Picture URL"]
                    writer = csv.DictWriter(file, fieldnames=fieldnames)

                    writer.writeheader()  
                    writer.writerows(rows) 

                print(f"Saved {len(rows)} entries to {filename}")
                return render_template('instagram_scraper.html', filename=filename.split('/')[-1])
            else:
                print("No valid rows to save.")
                return render_template('instagram_scraper.html', error="No valid data found.")
        else:
            print("No data found or there was an error fetching the data.")
            return render_template('instagram_scraper.html', error="No data found for the query.")

    return render_template('instagram_scraper.html')

@app.route('/download/search/<filename>')
def download_search(filename):
    file_path = os.path.join(FINAL_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Error: File not found.", 404


@app.route('/upload_csv', methods=['GET', 'POST'])
def process_username_csv():
    if request.method == 'POST':
        if 'csv_file' in request.files:
            file = request.files['csv_file']
            
            if file.filename.endswith('.csv'):
                upload_folder = FINAL_FOLDER
                os.makedirs(upload_folder, exist_ok=True)
                filename = os.path.join(upload_folder, file.filename)
                file.save(filename)

                try:
                    print(f"Processing CSV file: {filename}")
                   
                    result_file = process_usernames_from_csv(filename) 

                    if not os.path.exists(result_file):
                        return f"Error: Processed CSV file {result_file} not found.", 500

                    return render_template('csv.html', filename=os.path.basename(result_file))

                except Exception as e:
                    print(f"An error occurred: {e}")
                    return f"An error occurred: {e}", 500
            else:
                return "Error: Please upload a valid CSV file.", 400
        else:
            return "Error: No file provided.", 400

    return render_template('csv.html')

@app.route('/download/upload/<filename>')
def download_upload(filename):
    file_path = os.path.join(FINAL_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Error: File not found.", 404

if __name__ == '__main__':
    app.run(debug=True)
