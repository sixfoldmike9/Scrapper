import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse as urlparse
from urllib.parse import urljoin

def scrape_documents_from_page(page_url, output_file, terminal_output_file, urls_file):
    try:
        # Send a GET request to the page URL
        page_response = requests.get(page_url)
        # Check if the GET request was successful
        if page_response.status_code == 200:
            # Parse the response HTML using BeautifulSoup
            page_soup = BeautifulSoup(page_response.text, 'html.parser')

            # Extract all the links from the page
            links = page_soup.find_all('a', href=True)

            # Iterate through each link
            for link in links:
                # Extract the URL of the linked page
                linked_page_url = urljoin(page_url, link['href'])

                # Check if the link points to a document
                if 'doctypes' in linked_page_url:
                    # Send a GET request to the document URL
                    document_response = requests.get(linked_page_url)
                    # Check if the GET request was successful
                    if document_response.status_code == 200:
                        # Parse the response HTML using BeautifulSoup
                        document_soup = BeautifulSoup(document_response.text, 'html.parser')

                        # Extract the text from the document
                        document_text_div = document_soup.find('div', class_='judgments')
                        if document_text_div:
                            document_text = document_text_div.get_text(strip=True)

                            # Write the URL to the URLs CSV file
                            with open(urls_file, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow([linked_page_url])

                            # Write the extracted text to the output CSV file
                            with open(output_file, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow([document_text])
                        else:
                            print(f"Failed to find 'judgments' div in page: {linked_page_url}")
                    else:
                        print(f"Failed to retrieve page content from: {linked_page_url}. Status code: {document_response.status_code}")

            # Check if there is a "Next" link at the bottom of the page
            next_link = page_soup.find('a', text='Next')
            if next_link:
                # Extract the URL of the next page
                next_page_url = urljoin(page_url, next_link['href'])
                # Scrape documents from the next page
                scrape_documents_from_page(next_page_url, output_file, terminal_output_file, urls_file)
        else:
            print(f"Failed to retrieve page content from: {page_url}. Status code: {page_response.status_code}")
    except Exception as e:
        print(f"Error occurred while scraping page {page_url}: {str(e)}")

# Define the main page URL
main_page_url = 'https://indiankanoon.org/search/?formInput=doctypes:gauhati%20fromdate:1-1-1948%20todate:%2031-12-1948'

# Output file for URLs and extracted text
output_file = 'output3.csv'
terminal_output_file = 'terminal_output.csv'
urls_file = 'urls.csv'

# Scrape documents from the main page
scrape_documents_from_page(main_page_url, output_file, terminal_output_file, urls_file)