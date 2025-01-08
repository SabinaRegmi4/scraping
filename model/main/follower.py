import requests
import csv

url = "https://instagram-scraper-api2.p.rapidapi.com/v1/followers"
headers = {
    "x-rapidapi-key": "bc22e7587amshfc4d00fd8b7d2d5p177e78jsna0396e0bb76e",
    "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
}

def save_to_csv(data, filename="followers_data.csv"):
    fieldnames = ['username', 'full_name', 'profile_picture', 'bio', 'website']
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()

        writer.writerows(data)

def fetch_followers_with_pagination(username, output_file):
    querystring = {"username_or_id_or_url": username}
    all_followers = []
    pagination_token = None

    while True:
        if pagination_token:
            querystring['pagination_token'] = pagination_token

        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()

            print("API Response:", data)

            if 'data' in data and 'items' in data['data']:
                followers = data['data']['items']
                print(f"Fetched {len(followers)} followers on this page.")

                for follower in followers:
                    all_followers.append({
                        'username': follower.get('username', ''),
                        'full_name': follower.get('full_name', ''),
                        'profile_picture': follower.get('profile_picture', ''),
                        'bio': follower.get('bio', ''),
                        'website': follower.get('website', ''),
                    })

                pagination_token = data['data'].get('pagination_token', None)
                if pagination_token:
                    print(f"Next page exists, fetching more followers...")
                else:
                    print("No more pages to fetch.")
                    break
            else:
                print("No followers data found in the response.")
                break
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            break
    save_to_csv(all_followers, filename=output_file)
    print(f"Fetched and saved {len(all_followers)} followers to {output_file}")

if __name__ == "__main__":
    username = "socialtownmarketing"  
    output_csv = "followers_usernames.csv"
    fetch_followers_with_pagination(username, output_csv)
