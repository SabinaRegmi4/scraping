import time
import requests
import csv

def get_instagram_data(username):
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
    querystring = {"username_or_id_or_url": username}
    headers = {
        "x-rapidapi-key": "bc22e7587amshfc4d00fd8b7d2d5p177e78jsna0396e0bb76e",
        "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
    }
    
    retries = 5
    for attempt in range(retries):
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:
            print(f"Rate limit exceeded. Retrying after {2 ** attempt} seconds...")
            time.sleep(2 ** attempt)

        print(f"Error {response.status_code}: {response.text}")
        break
    return None

def save_to_csv(data, filename):
    if data:
        # Add 'username' explicitly to ensure it appears as a field in the CSV
        headers = ['username'] + list(data.keys())
        
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            
            # Create a dictionary with 'username' included as the first field
            user_data = {'username': data.get('username', '')}
            user_data.update(data)  # Add the rest of the data
            
            writer.writerow(user_data)
            print(f"Data saved to {filename}")
    else:
        print("No data to save.")

username = "vaguzenergy"
data = get_instagram_data(username)

if data:
    print("Retrieved Data:", data)
    save_to_csv(data, 'instagram_data.csv') 
else:
    print("Failed to retrieve data.")
