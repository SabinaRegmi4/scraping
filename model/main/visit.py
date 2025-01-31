# import requests
# import csv
# import time
# import os

# API_URL = "https://website-social-scraper-api.p.rapidapi.com/contacts"
# # HEADERS = {
# #     "x-rapidapi-key": "bc22e7587amshfc4d00fd8b7d2d5p177e78jsna0396e0bb76e",
# #     "x-rapidapi-host": "website-social-scraper-api.p.rapidapi.com"
# # }
# HEADERS = {
#             'x-rapidapi-key': "d3934419c0msh3b8edd6763061d0p1cee13jsnc9318ca42d50",
#             'x-rapidapi-host': "website-social-scraper-api.p.rapidapi.com"
#         }

# input_directory = "model/output/clean-output/"
# output_directory = "model/output/semi-output/"

# def get_website_details(website):
#     try:
#         querystring = {"website": website}
#         response = requests.get(API_URL, headers=HEADERS, params=querystring)
#         response.raise_for_status()  
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching data for {website}: {e}")
#         return None

# def read_websites_from_csv(file_path):
#     data = []
#     with open(file_path, "r", encoding="utf-8") as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             if row["Website"]:  
#                 data.append(row)
#     return data

# def save_results_to_csv(file_path, results):
#     with open(file_path, "w", newline="", encoding="utf-8") as file:
#         fieldnames = ["Query", "Country", "Name", "Phone", "Website", "Emails", "Phones", "LinkedIn", "Twitter", "Facebook", "Instagram"]
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         writer.writeheader()
#         for result in results:
#             writer.writerow(result)
#     print(f"Results saved to {file_path}")

# def process_csv_files():
#     for input_file in os.listdir(input_directory):
#         if input_file.endswith(".csv"):
#             input_file_path = os.path.join(input_directory, input_file)
#             output_file_path = os.path.join(output_directory, input_file)

#             if not os.path.exists(input_file_path):
#                 print(f"Input file not found: {input_file_path}")
#                 continue

#             print(f"Processing file: {input_file}")
#             data = read_websites_from_csv(input_file_path)
#             results = []

#             for entry in data:
#                 website = entry["Website"]
#                 print(f"Fetching details for: {website}")
#                 api_data = get_website_details(website)

#                 if api_data:
#                     entry.update({
#                         "Emails": ", ".join(api_data.get("emails", [])),
#                         "Phones": ", ".join(api_data.get("phones", [])) if api_data.get("phones") else entry["Phone"],  # Keep existing phone if no new data
#                         "LinkedIn": api_data.get("linkedin", ""),
#                         "Twitter": api_data.get("twitter", ""),
#                         "Facebook": api_data.get("facebook", ""),
#                         "Instagram": api_data.get("instagram", ""),
#                     })
#                 else:
#                     entry.update({
#                         "Emails": "",
#                         "Phones": entry["Phone"],  
#                         "LinkedIn": "",
#                         "Twitter": "",
#                         "Facebook": "",
#                         "Instagram": "",
#                     })

#                 results.append(entry)
#                 time.sleep(1) 

#             save_results_to_csv(output_file_path, results)

# if __name__ == "__main__":
#     process_csv_files()

import requests
import csv
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEYS = os.getenv("API_KEYS", "").split(",")

API_URL = "https://website-social-scraper-api.p.rapidapi.com/contacts"
# API_KEYS = [
#     "d3934419c0msh3b8edd6763061d0p1cee13jsnc9318ca42d50",  
#     "bc22e7587amshfc4d00fd8b7d2d5p177e78jsna0396e0bb76e",
#     "e322255979msh75be123a8612a09p1c1ff6jsnb97207a9be79",
   
# ]
current_api_key_index = 0 

input_directory = "model/output/clean-output/"
output_directory = "model/output/semi-output/"

def get_website_details(website):
    global current_api_key_index
    
    while True:
        try:
            headers = {
                'x-rapidapi-key': API_KEYS[current_api_key_index],
                'x-rapidapi-host': "website-social-scraper-api.p.rapidapi.com"
            }
            querystring = {"website": website}
            response = requests.get(API_URL, headers=headers, params=querystring)

            if response.status_code == 429:
                print(f"Rate limit exceeded with API key {API_KEYS[current_api_key_index]}. Switching key.")
                current_api_key_index = (current_api_key_index + 1) % len(API_KEYS) 
                time.sleep(10) 
                continue  

            response.raise_for_status()  

            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {website}: {e}")
            return None

def read_websites_from_csv(file_path):
    data = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Website"]:  
                data.append(row)
    return data

def save_results_to_csv(file_path, results):
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        fieldnames = ["Query", "Country", "Name", "Phone", "Website", "Emails", "Phones", "LinkedIn", "Twitter", "Facebook", "Instagram"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    print(f"Results saved to {file_path}")

def process_csv_files():
    for input_file in os.listdir(input_directory):
        if input_file.endswith(".csv"):
            input_file_path = os.path.join(input_directory, input_file)
            output_file_path = os.path.join(output_directory, input_file)

            if not os.path.exists(input_file_path):
                print(f"Input file not found: {input_file_path}")
                continue

            print(f"Processing file: {input_file}")
            data = read_websites_from_csv(input_file_path)
            results = []

            for entry in data:
                website = entry["Website"]
                print(f"Fetching details for: {website}")
                api_data = get_website_details(website)

                if api_data:
                    entry.update({
                        "Emails": ", ".join(api_data.get("emails", [])),
                        "Phones": ", ".join(api_data.get("phones", [])) if api_data.get("phones") else entry["Phone"],  # Keep existing phone if no new data
                        "LinkedIn": api_data.get("linkedin", ""),
                        "Twitter": api_data.get("twitter", ""),
                        "Facebook": api_data.get("facebook", ""),
                        "Instagram": api_data.get("instagram", ""),
                    })
                else:
                    entry.update({
                        "Emails": "",
                        "Phones": entry["Phone"],  
                        "LinkedIn": "",
                        "Twitter": "",
                        "Facebook": "",
                        "Instagram": "",
                    })

                results.append(entry)
                time.sleep(1) 

            save_results_to_csv(output_file_path, results)

if __name__ == "__main__":
    process_csv_files()
