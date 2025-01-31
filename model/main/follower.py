
import requests
import csv
import os
import time
from dotenv import load_dotenv

load_dotenv()
api_keys = os.getenv("API_KEYS").split(',')

# api_keys = [
#     "e322255979msh75be123a8612a09p1c1ff6jsnb97207a9be79",
#     "d3934419c0msh3b8edd6763061d0p1cee13jsnc9318ca42d50",
#     "bc22e7587amshfc4d00fd8b7d2d5p177e78jsna0396e0bb76e",
#     "6d2defe78bmsh7e094e2b3b71010p17fdd3jsn71af253bffe6",
#     "e322255979msh75be123a8612a09p1c1ff6jsnb97207a9be79",
#     "a13081d976mshc77eed73ce80453p106294jsn69bc0f147f93"
  
# ]
def get_next_api_key(index, max_attempts):
    index += 1
    if index >= max_attempts:
        print("All API keys exhausted. Could not fetch followers.")
        return None, index
    return index, api_keys[index % len(api_keys)]


def save_to_csv(followers, username):
   
    filename = f"model/insta/{username}_followers.csv"  
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    fieldnames = ['username', 'full_name', 'profile_pic_url', 'latest_story_ts', 'bio', 'website', 'id', 'is_verified', 'is_private']
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerows(followers)
        print(f"Saving file to: {filename}")

    print(f"Saved {len(followers)} followers to {filename}")

def fetch_followers(username):
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/followers"
    querystring = {"username_or_id_or_url": username}
    followers = []  
    api_key_index = 0  
    max_attempts = len(api_keys) 
    attempts = 0 

    while True:
        headers = {
            'x-rapidapi-key': api_keys[api_key_index],
            "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code == 429:  
            print("Rate limit exceeded. Switching to the next API key...")
            api_key_index, _ = get_next_api_key(api_key_index, max_attempts)
            if not api_key_index:
                break
            continue
        if response.status_code == 200:
            data = response.json() 
            if 'data' in data and 'items' in data['data']:
                current_page_followers = data['data']['items']
                print(f"Fetched {len(current_page_followers)} followers on this page.")
                followers.extend(current_page_followers)

                pagination_token = data.get('pagination_token')
                if pagination_token:
                    querystring["pagination_token"] = pagination_token
                else:
                    print("No more followers to fetch.")
                    break
            else:
                print("No followers data found in the response.")
                break
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break

        time.sleep(1)  

    if followers:
        save_to_csv(followers, username)
        print(f"Total followers fetched: {len(followers)}")
    else:
        print("No followers were fetched.")

if __name__ == "__main__":
    username = input("Enter the Instagram username: ")  
    fetch_followers(username)






