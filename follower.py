import time
import requests
import csv

def get_instagram_data(username):
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
    querystring = {"username_or_id_or_url": username}
    headers = {
        'x-rapidapi-key': "d3934419c0msh3b8edd6763061d0p1cee13jsnc9318ca42d50",
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

def save_relevant_data_to_csv(data, filename="usernames.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Full Name", "Public Email", "Contact Email", "URL"]) 

        for user in data:
            writer.writerow([user.get("username", ""), user.get("full_name", ""),
                             user.get("public_email", ""), user.get("contact_email", ""), user.get("url", "")])

username = "vaguzenergy"
data = get_instagram_data(username)

if data and 'data' in data and isinstance(data['data'], dict):
    print(data)  

    items = data['data'].get('items', [])
    relevant_data = []

    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                url = item.get("url")
                if url:
                    user_data = get_instagram_data(url) 

                    if user_data and 'data' in user_data and isinstance(user_data['data'], dict):
                        user_info = {
                            "username": user_data['data'].get("username", ""),
                            "full_name": user_data['data'].get("full_name", ""),
                            "url": user_data['data'].get("url", ""),
                            "public_email": user_data['data'].get("public_email", ""), 
                            "contact_email": user_data['data'].get("contact_email", "")  
                        }
                        relevant_data.append(user_info)

        if relevant_data:
            save_relevant_data_to_csv(relevant_data)
        else:
            print("No relevant data found.")
    else:
        print("The 'items' field is not a list or is missing.")
else:
    print("Failed to retrieve data.")
