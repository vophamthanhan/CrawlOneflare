from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re

category_url = "https://www.oneflare.com.au/air-conditioning"
driver = webdriver.Chrome()  
driver.maximize_window()
driver.get(category_url)

print("Loading category page...")
time.sleep(60)

# Collect all href links
links = driver.find_elements(By.XPATH, "/html/body/div[1]/section[4]/ul/li/h3/a")
hrefs = [link.get_attribute('href') for link in links]
print(f"Found {len(hrefs)} business links.")

data = []
def extract_data(url):
    driver.get(url)
    time.sleep(3)
    try:
        business_name = driver.find_element(By.XPATH, "//h1").text
    except:
        business_name = "N/A"
    try:
        number_of_jobs = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/section[1]/section/section[1]/p")
        text = number_of_jobs.text
        match = re.search(r'\d+', text)
        if match:
            jobs_completed = match.group()
        else:
            jobs_completed = "N/A"
    except:
        jobs_completed = "N/A"
    try:
        phone_element = driver.find_element(By.XPATH, '//a[@data-tooltip-content="Click to show number"]')
        phone_element.click()
        phone_number = phone_element.text
    except:
        phone_number = "N/A"
    try:
        website_url = "N/A"
        elements = driver.find_elements(By.CLASS_NAME, "sc-906e671e-5.bQwqNJ")
        for element in elements:
            text = element.text
            if "Website:" in text:
                website_url = text.split("Website:")[1].strip()
                break
    except:
        website_url = "N/A"
    try:
        address = "N/A"
        elements = driver.find_elements(By.CLASS_NAME, "sc-906e671e-5.bQwqNJ")
        for element in elements:
            text = element.text
            if "Address:" in text:
                address = text.split("Address:")[1].strip()
                break
    except:
        address = "N/A"
    return {
        "Business Name": business_name,
        "Number of Jobs Completed": jobs_completed,
        "Phone Number": phone_number,
        "Website URL": website_url,
        "Address": address,
    }

for url in hrefs:
    try:
        print(f"Processing: {url}")
        record = extract_data(url)
        record["URL"] = url
        data.append(record)
    except Exception as e:
        print(f"Error processing {url}: {e}")

# Save to Excel
output_file = "business_data.xlsx"
df = pd.DataFrame(data)
df.to_excel(output_file, index=False)
print(f"Data extraction complete. Saved to {output_file}")

driver.quit()
