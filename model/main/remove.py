import pandas as pd
import os
import re

def clean_and_save_csv(input_dir, clean_output_dir, target_file):
    try:
        if not os.path.exists(clean_output_dir):
            os.makedirs(clean_output_dir)

        input_path = os.path.join(input_dir, target_file)
        
        clean_output_path = os.path.join(clean_output_dir, target_file)

        print(f"Cleaning CSV file: {input_path}")
        try:
            df = pd.read_csv(input_path)  
        except Exception as e:
            print(f"Error reading CSV file {input_path}: {str(e)}")
            return None

        if 'Emails' not in df.columns:
            print(f"'Emails' column not found in {input_path}. Skipping this file.")
            return None

        print(f"Initial rows in {target_file}: {len(df)}")

        df_cleaned = df.dropna(subset=['Emails']) 
        print(f"Rows after dropping NaN emails: {len(df_cleaned)}")

        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")  

        df_cleaned = df_cleaned[df_cleaned['Emails'].apply(lambda x: bool(email_pattern.match(str(x))))]  
        print(f"Rows after filtering valid emails: {len(df_cleaned)}")

        if 'Website' in df.columns:
            url_pattern = re.compile(
                r'^(https?://)?(www\.)?([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,}(/.*)?$'
            )

            df_cleaned = df_cleaned[df_cleaned['Website'].apply(lambda x: bool(url_pattern.match(str(x))))]  
            print(f"Rows after filtering valid URLs: {len(df_cleaned)}")

            df_cleaned = df_cleaned.dropna(subset=['Website'])
            print(f"Rows after dropping NaN in Website column: {len(df_cleaned)}")

        try:
            df_cleaned.to_csv(clean_output_path, index=False)
            print(f"Saved cleaned CSV file to: {clean_output_path}")
            return clean_output_path 
        except Exception as e:
            print(f"Error saving cleaned CSV file to {clean_output_path}: {str(e)}")
            return None
    except Exception as e:
        print(f"Error in clean_and_save_csv: {str(e)}")
        raise

input_dir = r'model/output/semi-output'  
clean_output_dir = r'model/output/final-output'  

if __name__ == "__main__":
    for file in os.listdir(input_dir):
        if file.endswith('.csv'):
            clean_and_save_csv(input_dir, clean_output_dir, file)
