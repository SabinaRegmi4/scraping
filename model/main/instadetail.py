import time
import requests
import csv
import re
import os
from dotenv import load_dotenv

load_dotenv()

api_keys = os.getenv("API_KEYS", "").split(",")

# api_keys = [
#     "d678a03957mshd2c346f917d2a45p1ada1ejsn522aba081fef",
#     "e322255979msh75be123a8612a09p1c1ff6jsnb97207a9be79",
#     "6d2defe78bmsh7e094e2b3b71010p17fdd3jsn71af253bffe6",
#     "d3934419c0msh3b8edd6763061d0p1cee13jsnc9318ca42d50",
#     "bc22e7587amshfc4d00fd8b7d2d5p177e78jsna0396e0bb76e",
#     "a13081d976mshc77eed73ce80453p106294jsn69bc0f147f93"
# ]

def get_next_api_key():
    if len(api_keys) == 0:
        raise Exception("No API keys available.")
    key = api_keys.pop(0)
    api_keys.append(key)
    return key

def get_instagram_data(username, api_key):
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
    querystring = {"username_or_id_or_url": username}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
    }

    retries = 5
    for attempt in range(retries):
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            print(f"Data retrieved for {username}")
            data = response.json().get('data', {})
            if not data:
                print(f"No data returned for {username}")
            return data
        elif response.status_code == 429:
            print(f"Rate limit exceeded. Retrying after {2 ** attempt} seconds...")
            time.sleep(2 ** attempt)
        else:
            print(f"Error {response.status_code}: {response.text}")
            break
    return None

def extract_important_details(data):
    if not data:
        return {}

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, data.get('public_email', '') + " " + data.get('external_url', ''))

    phone_number = data.get('public_phone_number', '')
    work_related_urls = []

    if data.get('bio_links'):
        work_related_urls.extend(link['url'] for link in data['bio_links'] if 'url' in link)

    if data.get('external_url'):
        work_related_urls.append(data['external_url'])

    return {
        "username": data.get('username', ''),
        "full_name": data.get('full_name', ''),
        "emails": ", ".join(set(emails)),
        "website": ", ".join(work_related_urls),
        "phone_number": phone_number
    }

def save_to_csvs(data, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving data to {output_file}: {e}")
def process_usernames_from_csv(input_file):
    OUTPUT_FOLDER = 'model/insta'
    FINAL_FOLDER = 'model/insta/output'

    output_file = os.path.join(FINAL_FOLDER, f"{os.path.basename(input_file).replace('.csv', '_output.csv')}")

    try:
        with open(input_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"Fieldnames in CSV: {reader.fieldnames}")

            if 'username' not in reader.fieldnames:
                raise ValueError(f"'username' column is missing in the file: {input_file}")

            for row in reader:
                username = row.get('username')
                if username:
                    print(f"Processing username: {username}")
                    api_key = get_next_api_key()
                    data = get_instagram_data(username, api_key)
                    if data:
                        important_data = extract_important_details(data)
                        save_to_csvs(important_data, output_file)
                    else:
                        print(f"Failed to retrieve data for {username}")
    except Exception as e:
        print(f"An error occurred while processing CSV {input_file}: {str(e)}")

    print(f"Instagram data processing completed for {input_file}!")
    return output_file



if __name__ == '__main__':
    process_usernames_from_csv()
