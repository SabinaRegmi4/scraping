import requests
import csv
import time


url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
headers = {
    "x-rapidapi-key": "bc22e7587amshfc4d00fd8b7d2d5p177e78jsna0396e0bb76e",
    "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
}

def save_user_details_to_csv(data, filename="user_details.csv"):
    fieldnames = ['username', 'full_name', 'profile_picture', 'bio', 'website', 'email', 'contact']
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()

        writer.writerows(data)

def fetch_user_details(usernames, output_file):
    all_user_details = []

    for username in usernames:
        print(f"Fetching details for {username}")
        querystring = {"username_or_id_or_url": username}

        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status() 
            data = response.json()

            if 'data' in data:
                user_data = data['data']
                all_user_details.append({
                    'username': user_data.get('username', ''),
                    'full_name': user_data.get('full_name', ''),
                    'profile_picture': user_data.get('profile_picture', ''),
                    'bio': user_data.get('bio', ''),
                    'website': user_data.get('website', ''),
                    'email': "",  
                    'contact': ""
                })
            else:
                print(f"No data found for {username}")

            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"Error during request for {username}: {e}")

    save_user_details_to_csv(all_user_details, filename=output_file)
    print(f"Fetched and saved {len(all_user_details)} user details to {output_file}")


def read_usernames_from_csv(file_path):
    usernames = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"]:
                usernames.append(row["username"]) 
    return usernames

if __name__ == "__main__":
    input_csv = "followers_usernames.csv"  
    output_csv = "user_details.csv"  

    usernames = read_usernames_from_csv(input_csv)

    fetch_user_details(usernames, output_csv)
