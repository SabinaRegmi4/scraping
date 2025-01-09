import os
import time
import random
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def human_scroll(driver, scroll_pause=0.5):
    """Simulates human-like scrolling behavior."""
    for _ in range(random.randint(2, 5)):  
        scroll_height = random.randint(200, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(scroll_pause + random.uniform(0.2, 0.5))


def hover_and_click(driver, element):
    """Simulates a hover over an element before clicking."""
    try:
        actions = ActionChains(driver)
        actions.move_to_element(element).pause(random.uniform(0.5, 1.5)).click().perform()
    except Exception as e:
        print(f"Failed to hover and click: {e}")


def extract(driver):
    """Extract company details."""
    company_data = {"Name": "", "Phone": "", "Website": ""}
    
    try:
        company_name_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@class='rgnuSb tZPcob']"))
        )
        company_data["Name"] = company_name_element.text
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Company name element not found: {e}")
    
    try:
        company_phone_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@class='eigqqc']"))
        )
        company_data["Phone"] = company_phone_element.text
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Company phone element not found: {e}")
        
    try:
        company_website_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@class='Gx8NHe']"))
        )
        company_data["Website"] = company_website_element.get_attribute('href') or company_website_element.text
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Company website element not found: {e}")
    
    return company_data
def scrape_search_query(search_query, country):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-features=Translate")
    chrome_options.add_argument('--lang=en-US')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--start-maximized")

    driver = uc.Chrome(options=chrome_options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});")

    output_folder = os.path.join("model", "output", "raw-output")
    os.makedirs(output_folder, exist_ok=True)

    filename = f"{search_query.replace(' ', '_').lower()}_{country.lower()}.csv"
    file_path = os.path.join(output_folder, filename)

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Query", "Country", "Name", "Phone", "Website"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    links = [
        {
            "url": "https://www.google.com/localservices/prolist?g2lbs=AOHF13mhHibc8vhc4Phwek7HQjY1BuO4-fIa26UI_Q2Qz5P7036IttVGU6t3TGXmUrXjq64ql-SS&hl=en-NP&gl=np&cs=1&ssta=1&oq=Yoga%20in%20Belgium&src=2&sa=X&q=Yoga%20in%20Belgium&ved=0CAUQjdcJahcKEwj4qqWgrMWKAxUAAAAAHQAAAAAQZA&scp=ChBnY2lkOnlvZ2Ffc3R1ZGlvEgAaACoLWW9nYSBzdHVkaW8%3D&slp=MgBAAVIECAIgAIgBAJoBBgoCFxkQAA%3D%3D",
        }
    ]

    for item in links:
        link = item["url"]
        updated_url = link.replace("Yoga%20in%20Belgium", search_query.replace(" ", "%20"))
        updated_url = updated_url.replace("Belgium", country)

        try:
            driver.get(updated_url)
            print(f"Processing country: {country}")
            time.sleep(random.uniform(3, 5))

            human_scroll(driver)

            while True:
                try:
                    companies = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//*[@class='DVBRsc']"))
                    )
                except TimeoutException as e:
                    print(f"No companies found on the page for {country}: {e}")
                    break

                for company in companies:
                    try:
                        hover_and_click(driver, company)
                        time.sleep(random.uniform(3, 5))
                        company_data = extract(driver)
                        company_data["Country"] = country
                        company_data["Query"] = search_query

                        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=["Query", "Country", "Name", "Phone", "Website"])
                            writer.writerow(company_data)
                        print(f"Scraped data for company: {company_data['Name']}")

                        driver.back()
                        time.sleep(random.uniform(2, 4))
                    except Exception as e:
                        print(f"Error occurred while processing company: {e}")

                try:
                    next_button = WebDriverWait(driver, 13).until(
                        EC.element_to_be_clickable((By.XPATH, "(//span[text()='Next >'])[1]"))
                    )
                    hover_and_click(driver, next_button)
                    time.sleep(random.uniform(5, 10))

                except (NoSuchElementException, TimeoutException) as e:
                    print(f"No 'Next' button found or last page reached for {country}: {e}")
                    break

        except Exception as e:
            print(f"Error occurred for link {link} ({country}): {e}")

    driver.quit()
    print(f"Scraping completed. Data saved to {file_path}.")
    return filename 
