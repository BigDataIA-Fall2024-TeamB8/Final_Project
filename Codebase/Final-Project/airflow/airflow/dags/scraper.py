from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from chromedriver_py import binary_path
from bs4 import BeautifulSoup
import time
import json
import boto3

# Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")

# Global variables
max_page = 300
sleep_time = 1
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("window-size=1900,800")

# S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def get_browser():
    service = Service(executable_path=binary_path)
    wd = webdriver.Chrome(service=service, options=chrome_options)
    return wd

def scrape_ted_talks():
    browser = get_browser()
    
    def talks_page():
        url = 'https://www.ted.com/talks?sort=newest'
        browser.get(url)
        time.sleep(sleep_time * 4)
        try:
            cookie_btn = browser.find_element(By.ID, 'onetrust-accept-btn-handler')
            cookie_btn.click()
        except:
            pass
        time.sleep(sleep_time)

    talks_page()

    final = []
    for page in range(0, max_page):
        payload = [{
            "indexName": "newest",
            "params": {
                "attributeForDistinct": "objectID",
                "distinct": 1,
                "facets": ["subtitle_languages", "tags"],
                "highlightPostTag": "__/ais-highlight__",
                "highlightPreTag": "__ais-highlight__",
                "hitsPerPage": 24,
                "maxValuesPerFacet": 500,
                "page": page,
                "query": "",
                "tagFilters": ""
            }
        }]

        r = requests.post('https://zenith-prod-alt.ted.com/api/search',
                          headers={'Content-type': 'application/json; charset=UTF-8',
                                   "User-Agent": "curl/7.64.1"},
                          json=payload)
        if r.status_code == 200:
            my_tedx = r.json()['results'][0]["hits"]
            final.extend(my_tedx)
        else:
            print(f"Error: {r.status_code} on page {page}")
        time.sleep(sleep_time)

    final_list = []
    for talk in final:
        slug = talk["slug"]
        final_list.append({
            'id': talk["objectID"],
            'slug': talk["slug"],
            'speakers': talk["speakers"],
            'title': talk["title"],
            'url': f'https://www.ted.com/talks/{slug}'
        })

    pd.DataFrame(final_list).to_csv('/tmp/ted_talks_list.csv', index=False)
    browser.quit()

def scrape_transcripts():
    df = pd.read_csv('/tmp/ted_talks_list.csv')

    if "transcript" not in df.columns:
        df["transcript"] = ""

    def extract_transcript_from_page(url):
        try:
            response = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                script_tag = soup.find("script", type="application/ld+json")
                if script_tag:
                    data = json.loads(script_tag.string)
                    transcript = data.get("transcript")
                    if transcript:
                        return transcript

                transcript_sections = soup.find_all("div", class_="Grid__cell")
                transcript = " ".join([section.text.strip() for section in transcript_sections])
                if transcript:
                    return transcript
            else:
                print(f"Failed to fetch {url}. Status code: {response.status_code}")
                return ""
        except Exception as e:
            print(f"Error fetching transcript for {url}: {e}")
            return ""

    for index, row in df.iterrows():
        if pd.isna(row["transcript"]) or not row["transcript"]:
            transcript = extract_transcript_from_page(row["url"])
            df.at[index, "transcript"] = transcript
        time.sleep(2)

    df.to_csv('/tmp/ted_talks_transcripts_updated.csv', index=False)

def upload_to_s3():
    df = pd.read_csv('/tmp/ted_talks_transcripts_updated.csv')

    df.columns = df.columns.str.strip().str.lower()

    if "transcript" not in df.columns:
        raise KeyError("The 'transcript' column does not exist in the CSV file. Please verify the file.")

    for _, row in df.iterrows():
        if pd.isna(row["transcript"]):
            continue

        metadata = {
            "id": int(row["id"]) if "id" in row and not pd.isna(row["id"]) else None,
            "slug": row["slug"] if "slug" in row and not pd.isna(row["slug"]) else None,
            "speakers": row["speakers"] if "speakers" in row and not pd.isna(row["speakers"]) else None,
            "title": row["title"] if "title" in row and not pd.isna(row["title"]) else None,
            "url": row["url"] if "url" in row and not pd.isna(row["url"]) else None,
            "transcript": row["transcript"] if "transcript" in row and not pd.isna(row["transcript"]) else None,
        }

        folder_name = row["slug"] if "slug" in row and not pd.isna(row["slug"]) else f"talk_{row['id']}"
        file_name = "metadata.json"

        try:
            json_data = json.dumps(metadata, indent=4)
            s3_path = f"{folder_name}/{file_name}"
            s3_client.put_object(Bucket=S3_BUCKET, Key=s3_path, Body=json_data)
            print(f"Uploaded: {s3_path}")
        except Exception as e:
            print(f"Error uploading {file_name} to S3: {e}")

# Define the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ted_talks_scraper_and_uploader',
    default_args=default_args,
    description='A DAG to scrape TED Talks metadata and transcripts, and upload to S3',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 12, 1),
    catchup=False,
)

scrape_ted_talks_task = PythonOperator(
    task_id='scrape_ted_talks_metadata',
    python_callable=scrape_ted_talks,
    dag=dag,
)

scrape_transcripts_task = PythonOperator(
    task_id='scrape_ted_talks_transcripts',
    python_callable=scrape_transcripts,
    dag=dag,
)

upload_to_s3_task = PythonOperator(
    task_id='upload_transcripts_to_s3',
    python_callable=upload_to_s3,
    dag=dag,
)

scrape_ted_talks_task >> scrape_transcripts_task >> upload_to_s3_task
