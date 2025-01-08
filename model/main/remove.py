import os
import pandas as pd


clean_output_dir=os.path.join(os.path.dirname(__file__), 'model/output/semi-ouput')
final_output_dir = os.path.join(os.path.dirname(__file__), 'model/output/final-output')

def create_directories(clean_output_dir, final_output_dir):
    for directory in [clean_output_dir, final_output_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

def append_email_rows(df, final_output_filepath):
    email_columns = [col for col in df.columns if 'email' in col.lower()]
    if email_columns:
        df[email_columns] = df[email_columns].astype(str)
        email_rows = df[df[email_columns].apply(lambda x: x.str.contains('@')).any(axis=1)]
        if not email_rows.empty:
            if os.path.exists(final_output_filepath):
                email_rows.to_csv(final_output_filepath, mode='a', index=False, header=False)
            else:
                email_rows.to_csv(final_output_filepath, index=False)

def save_clean_rows(df, clean_output_filepath):
    email_columns = [col for col in df.columns if 'email' in col.lower()]
    if email_columns:
        df = df.copy()  
        df[email_columns] = df[email_columns].astype(str)
        df.loc[~df.index.isin(df[df[email_columns].apply(lambda x: x.str.contains('@')).any(axis=1)].index), email_columns] = ''
        df.to_csv(clean_output_filepath, index=False)


def process_csv_files(input_dir, final_output_dir, clean_output_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            try:
                filepath = os.path.join(input_dir, filename)
                df = pd.read_csv(filepath)
                
                df.drop_duplicates(inplace=True)
                
               
                df.dropna(inplace=True)
         
                final_output_filepath = os.path.join(final_output_dir, filename)
                append_email_rows(df, final_output_filepath)
                
               
                cleaned_filepath = os.path.join(clean_output_dir, filename)
                save_clean_rows(df, cleaned_filepath)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                
if __name__ == "__main__":
    create_directories(clean_output_dir, final_output_dir)
    
    print("Directories created successfully.")
    
    try:
        process_csv_files(clean_output_dir, final_output_dir,clean_output_dir)
        print("Processing completed successfully.")
    except Exception as e:
        print(f"Error during processing: {e}")
    else:
        print("Processing completed.")
