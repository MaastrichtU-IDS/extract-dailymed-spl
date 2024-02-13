import requests
import time
import json
import os 
import pdfkit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import csv 

DAILYMED_BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services"
SPLS_LIST_ENDPOINT = f"{DAILYMED_BASE_URL}/v2/spls.json"
XML_ENTRY_ENDPOINT = f"{DAILYMED_BASE_URL}/v2/spls/{{spl_set_id}}.xml"
HTML_ENTRY_ENDPOINT = f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={{spl_set_id}}"
PDF_ENTRY_ENDPOINT = f"https://dailymed.nlm.nih.gov/dailymed/getFile.cfm?setid={{spl_set_id}}&type=pdf"
SPL_FOLDER = f"/data/dailymed/spls"

def get_all_spls():
    spls = []
    page = 1
    while True:
        params = {
            'page': page,
            'limit': 100  # Assuming the maximum allowed is 100
        }
        response = requests.get(SPLS_LIST_ENDPOINT, params=params)
        response.raise_for_status()
        metadata = response.json().get('metadata',[])
        if not metadata:
            break
        data = response.json().get('data', [])
        if not data:
            break
        
        spls.extend(data)
        page += 1
        total_pages = metadata['total_pages']
        print(f"page: {page} of {total_pages}")
    return spls

def get_xml_entry(spl_set_id):
    response = requests.get(XML_ENTRY_ENDPOINT.format(spl_set_id=spl_set_id))
    response.raise_for_status()
    return response.text

def get_html_entry(spl_set_id):
    response = requests.get(HTML_ENTRY_ENDPOINT.format(spl_set_id=spl_set_id))
    response.raise_for_status()
    return response.text

def get_pdf_entry(spl_set_id):
    url = PDF_ENTRY_ENDPOINT.format(spl_set_id=spl_set_id)
    response = requests.get(url)
    return response

def save_spls_to_json(spls, filename=f"{SPL_FOLDER}/spls.json"):
    with open(filename, "w") as file:
        json.dump(spls, file, indent=4)

def load_spls_to_json(filename=f"{SPL_FOLDER}/spls.json"):
    with open(filename, "r") as f:
        j = json.load(f)
    return j




def generate_pdf_from_html(url, button_id, output_filename):
    # Set up the Selenium driver (assuming Chrome here, but you can use Firefox or others)

    options = Options()
    options.add_argument("headless=new")
    #options.add_argument("no-sandbox=True")

    homedir = os.path.expanduser("~")
    webdriver_service = Service(f"{homedir}/chromedriver/stable/chromedriver")
    browser = webdriver.Chrome(service=webdriver_service, options=options)
    browser.get(url)
    clickable = browser.find_element(By.ID, "anch_dj_109")
    ActionChains(browser).click(clickable).perform()
    html_content = browser.page_source
    #print(html_content)
    pdfkit_options = { 'javascript-delay':'5000'}
    pdfkit.from_string(html_content, output_filename, options = pdfkit_options)
    
    return None
    # Extract description from page and print
    description = browser.find_element(By.NAME, "description").get_attribute("content")
    print(f"{description}")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    

    clickable = driver.find_element(By.ID, "anch_dj_109")
    ActionChains(driver).click(clickable).perform()
    html_content = driver.page_source
    print(html_content)
    driver.quit()

    exit()  
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode
    with webdriver.Chrome(options=options) as driver:
        driver.get(url)

        # Find the button and click it
        button = driver.find_element_by_id(button_id)
        button.click()

        # Wait for the page to load after the click (you might need to adjust the sleep time)
        driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to become available

        # Get the final HTML after JavaScript execution
        html_content = driver.page_source

    # Convert the final HTML to PDF
    pdfkit.from_string(html_content, output_filename)

def get_pdf_entry_from_html(spl_set_id):
    url = HTML_ENTRY_ENDPOINT.format(spl_set_id=spl_set_id)
    return generate_pdf_from_html(url, "open-all", f"{SPL_FOLDER}/{spl_set_id}.pdf")

def load_group_by(filename):
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

def main():
    spls = load_group_by(f"/data/group_by.csv")

    # spl_file = f"{SPL_FOLDER}/spls.json"
    # if not os.path.isfile(spl_file):
    #     spls = get_all_spls()
    #     save_spls_to_json(spls)
    #     print(f"Saved {len(spls)} SPLs to {spl_file}")
    # else:
    #     spls = load_spls_to_json(spl_file)

    number = 1
    total = len(spls)
    for spl in spls:
        spl_set_id = spl.get('SETID')
        if spl_set_id:
            #get_pdf_entry_from_html(spl_set_id)
            pdf_file = f"{SPL_FOLDER}/pdf/{spl_set_id}.pdf"
            if not os.path.exists(pdf_file):
                response = get_pdf_entry(spl_set_id)
                if response.status_code != 200:
                    print(f"Unable to get PDF for {spl_set_id}")
                    continue

                with open(pdf_file, "wb") as file:
                    file.write(response.content)
                #print(f"Fetched PDF for SPL Set ID: {spl_set_id}")
            if number % 20 == 1:
                print(f'{number} of {total}')
            number +=1

if __name__ == "__main__":
    main()
