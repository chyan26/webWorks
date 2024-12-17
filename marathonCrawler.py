import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import json
import time
import pandas as pd
import requests

class MarathonCrawler:
    def __init__(self, data_dir='data'):
        self.driver = self.init_driver()
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def init_driver(self):
        options = uc.ChromeOptions()
        options.headless = True  # Disable headless mode for debugging
        driver = uc.Chrome(options=options)
        return driver

    def check_existing_data(self, bib_number):
        file_path = os.path.join(self.data_dir, f'{bib_number}.json')
        return os.path.exists(file_path)

    def load_existing_data(self, bib_number):
        file_path = os.path.join(self.data_dir, f'{bib_number}.json')
        with open(file_path, 'r') as f:
            return json.load(f)

    def save_data(self, bib_number, data):
        file_path = os.path.join(self.data_dir, f'{bib_number}.json')
        with open(file_path, 'w') as f:
            json.dump(data, f)

    def scrape_runner_data(self, url, bib_number, timeout=10, max_retries=3):
        if self.check_existing_data(bib_number):
            print(f"Data for bib number {bib_number} already exists. Skipping scraping.")
            return self.load_existing_data(bib_number)

        retries = 0
        while retries < max_retries:
            try:
                # Open the URL
                self.driver.get(url)
                
                # Wait for the page to load, or the Cloudflare challenge to appear
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'rank-card-athlete-name'))
                )

                # Add a delay to ensure the page is fully loaded
                time.sleep(2)

                # After bypassing the challenge, get the page source and parse it with BeautifulSoup
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Extract runner information
                runner_info = {'Bib Number': bib_number}
                
                # Extract name
                name_div = soup.find('div', class_='flex justify-content-between rank-card-athlete-name')
                if name_div:
                    name_h1 = name_div.find('h1', class_='fc-white float-left my-auto')
                    if name_h1:
                        runner_info['Name'] = name_h1.get_text(strip=True)
                
                # Extract other details
                info_div = soup.find('div', class_='flex text-align-left rank-card-detial float-left')
                if info_div:
                    spans = info_div.find_all('span', class_='fs-1')
                    if len(spans) >= 4:
                        runner_info['Event'] = spans[0].get_text(strip=True)
                        runner_info['Group'] = spans[1].get_text(strip=True)
                        runner_info['Nation'] = spans[2].get_text(strip=True)
                        runner_info['Gender'] = spans[3].get_text(strip=True)

                # Extract official and net times
                official_time_p = soup.find('p', class_='rankCard-text text-align-left grade')
                if official_time_p:
                    runner_info['Gun Time'] = official_time_p.get_text(strip=True)  # e.g., "02:11:41"

                net_time_p = soup.find('p', class_='rankCard-text main-color text-align-left grade')
                if net_time_p:
                    runner_info['Net Time'] = net_time_p.get_text(strip=True)  # e.g., "02:11:39"

                # Extract the JavaScript variable `record` from the page source
                script_tag = soup.find('script', string=lambda t: t and "var record =" in t)
                if script_tag:
                    script_content = script_tag.string
                    start_index = script_content.find("var record =") + len("var record =")
                    end_index = script_content.find("};", start_index) + 1

                    # Parse the JSON-like structure
                    raw_json = script_content[start_index:end_index].strip()
                    data = json.loads(raw_json)

                    # Modify CPAccumulate values where CPId > "04"
                    if "cp" in data:
                        for cp_id, cp_data in data["cp"].items():
                            if cp_id.isdigit() and int(cp_id) > 4:
                                cp_data["CPAccumulate"] -= 5780

                    result = {'runner_info': runner_info, 'record': data}
                    self.save_data(bib_number, result)
                    return result
                else:
                    print("'var record' not found in the page source.")
                    # Log the page source for debugging
                    with open(f'debug_{bib_number}.html', 'w') as f:
                        f.write(page_source)
                    return None

            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    print(f"Error: {e} after {max_retries} retries.")
                    return None
                else:
                    print(f"Retrying... ({retries}/{max_retries})")

    def close_driver(self):
        self.driver.quit()

def loop_through_bibs(base_url, output_file):
    crawler = MarathonCrawler()
    try:
        all_data = []
        max_404_count = 10

        for cart_number in range(1, 3):  # Cart numbers from 1 to 13
            error_count = 0
            max_run_number = 800  # Maximum run number for each cart number

            for run_number in range(1, max_run_number + 1):
                bib_number = f"{cart_number:03}{run_number:03}"  # Format bib number
                url = f"{base_url}{bib_number}"
                print(f"Fetching data for bib number: {bib_number}")

                data = crawler.scrape_runner_data(url, bib_number)

                if data:
                    all_data.append(data)
                    error_count = 0  # Reset error count after a successful fetch
                else:
                    # Check if the error was a 404 error
                    response = requests.get(url)
                    if response.status_code == 404:
                        error_count += 1
                        print(f"404 Error encountered for bib number: {bib_number}")
                    else:
                        print(f"Error encountered for bib number: {bib_number}")

                if error_count >= max_404_count:
                    print(f"Encountered {max_404_count} consecutive 404 errors. Moving to next cart number.")
                    break
        # Save all collected data to a JSON file
        with open(output_file, 'w') as json_file:
            json.dump(all_data, json_file, indent=4, ensure_ascii=False)

        print(f"All data saved to {output_file}")
  
    finally:
        crawler.close_driver()


def json_to_dataframe(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    records = []
    for entry in data:
        runner_info = entry['runner_info']
        record = entry['record']

        # Extract HM Time from cpid = 5
        hm_time = None
        if 'cp' in record and '5' in record['cp']:
            hm_time = record['cp']['5'].get('raceTime')

        records.append({
            'Bib Number': runner_info.get('Bib Number'),
            'Name': runner_info.get('Name'),
            'Group': runner_info.get('Group'),
            'Gender': runner_info.get('Gender'),
            'Net Time': runner_info.get('Net Time'),
            'HM Time': hm_time
        })

    df = pd.DataFrame(records)
    return df

# Base URL and output file
base_url = 'https://www.bravelog.tw/athlete/1189/'
output_file = 'all_runner_data.json'

loop_through_bibs(base_url, output_file)

# Convert JSON data to DataFrame
df = json_to_dataframe(output_file)
df.to_csv('2025_tpe_marathon.csv', index=False)
