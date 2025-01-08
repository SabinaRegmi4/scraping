import pandas as pd
import os
import logging
import re
import requests
from bs4 import BeautifulSoup

def extract_email_from_website(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url  

        if url.startswith('https://www.'):
            url = url.replace('www.', '') 

        response = requests.get(url, timeout=20)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        email = None
      
        email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
        match = email_pattern.search(soup.text)
        if match:
            email = match.group(0)
        return email
    except requests.RequestException as e:
        print(f"Error visiting {url}: {e}")
        return None

def clean_csv_files(input_dir, clean_output_dir):
    try:
        if not os.path.exists(clean_output_dir):
            os.makedirs(clean_output_dir)

        for csv_file in os.listdir(input_dir):
            if csv_file.endswith('.csv'):
                input_path = os.path.join(input_dir, csv_file)
                clean_output_path = os.path.join(clean_output_dir, csv_file)

                print(f"Cleaning CSV file: {input_path}")
                try:
                    df = pd.read_csv(input_path)
                except Exception as e:
                    print(f"Error reading CSV file {input_path}: {str(e)}")
                    continue

                if 'Website' in df.columns:
                    url_pattern = re.compile(
                        r'^(https?://)?(www\.)?([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,}(/.*)?$'
                    )

                    print(f"Initial rows in {csv_file}: {len(df)}")
                    df_cleaned = df[df['Website'].apply(lambda x: bool(url_pattern.match(str(x))))]
                    print(f"Rows after filtering valid URLs: {len(df_cleaned)}")

                    df_cleaned = df_cleaned.dropna(subset=['Website'])
                    print(f"Rows after dropping NaN: {len(df_cleaned)}")

                    if not df_cleaned.empty:
                        df_cleaned['Email'] = df_cleaned['Website'].apply(extract_email_from_website)

                    try:
                        df_cleaned.to_csv(clean_output_path, index=False)
                        print(f"Saved cleaned CSV file to: {clean_output_path}")
                    except Exception as e:
                        print(f"Error saving cleaned CSV file to {clean_output_path}: {str(e)}")
                else:
                    print(f"'Website' column not found in {input_path}. Skipping this file.")
    except Exception as e:
        print(f"Error in clean_csv_files: {str(e)}")
        raise



input_dir = r'model/output/raw-output'  
clean_output_dir = r'model/output/clean-output'  

if __name__ == "__main__":
    clean_csv_files(input_dir, clean_output_dir)
