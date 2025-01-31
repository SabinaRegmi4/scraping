import requests
import csv
import os
import time
from dotenv import load_dotenv

load_dotenv()
API_KEYS = os.getenv("API_KEYS").split(',')


API_URL = "https://instagram-scraper-api2.p.rapidapi.com/v1/search_users"
# HEADERS = {
#     "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com",
#     "x-rapidapi-key": "a13081d976mshc77eed73ce80453p106294jsn69bc0f147f93"
# }
current_api_key_index = 0 

FIELDNAMES = ["Username", "Full Name" ,"Email","Phone","Website","Followers", "Following", "Biography", "Profile Picture URL"]

def fetch_data(search_query):
    """Fetch data from the API for a specific query."""
    global current_api_key_index
    
    while True:
        try:  
            HEADERS = {
                "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com",
                "x-rapidapi-key": API_KEYS[current_api_key_index]
            }
            querystring = {"search_query": search_query} 
            response = requests.get(API_URL, headers=HEADERS, params=querystring)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  
                print(f"Rate limit exceeded with API key {API_KEYS[current_api_key_index]}. Switching key.")
                current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)  
                time.sleep(10) 
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return None
def save_to_csv(filename, rows):
    """Save rows to a CSV file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
        print(f"Saved {len(rows)} entries to {filename}")


if __name__ == "__main__":
    search_query = input("Enter the search query: ").strip()
    output_file = f"model/insta/output/{search_query.replace(' ', '_')}.csv"

    print(f"Fetching data for query: {search_query}")
    data = fetch_data(search_query)

    if data and "data" in data and "items" in data["data"]:
        rows = []
        for entry in data["data"]["items"]:
            if isinstance(entry, dict): 
                rows.append({
                    "Username": entry.get("username", ""),
                    "Full Name": entry.get("full_name", ""),
                    "Followers": entry.get("follower_count", ""),
                    "Following": entry.get("following_count", ""),
                    "Biography": entry.get("biography", ""),
                    "Profile Picture URL": entry.get("profile_pic_url", ""),
                })

        save_to_csv(output_file, rows)
    else:
        print("No data fetched or an error occurred.")

        print(f"Data fetching completed. Check the file: {output_file}")


