import threading
import requests
from bs4 import BeautifulSoup
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import re
import time
import os
import sqlite3

# Global set to store visited URLs to avoid visiting them again
visited_urls = set()
globalData = []
stopCrawling = False

proxies = { 
    "http"  : "192.168.0.106:7000", 
}
def crawl(url, depth):
    global globalData, stopCrawling, proxies

    if not url.startswith("http://"):
        return
    if depth <= 0 or stopCrawling:
        return
    if "support.google.com" in url:
        return
    if "accounts.google.com" in url:
        return
    if "youtube" in url:
        return
    # Add URL to visited set
    visited_urls.add(url)
    print(f"Crawling {url}")
    # Fetch the HTML content of the URL
    try:
        response = requests.get(url, proxies=proxies)
        if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
            html_content = response.text
        else:
            print(f"Failed to fetch {url}. Trying another link.")
            return
    except Exception as e:
        print(f"Error fetching {url}: {e}. Trying another link.")
        return
    
    # Extract title and tags
    soup = BeautifulSoup(html_content, 'html.parser')
    try:
        title = soup.title.string.strip() if soup.title else ""
    except:
        return
    tags = extract_tags_from_html(html_content, title)
    
    # Write data to JSON file
    data = {
        "url": url,
        "title": title,
        "tags": tags
    }

    if not data["url"]:
        return
    if not data["title"]:
        return
    if not data["tags"]:
        return

    if "youtube" in data["tags"] or "youtube" in data["title"]:
        return

    globalData.append(data)
    
    # Find new URLs
    for link in soup.find_all('a'):
        new_url = link.get('href')
        if new_url and new_url.startswith("http") and new_url not in visited_urls:
            # time.sleep(0.25)
            crawl(new_url, depth-1)


def extract_tags_from_html(html_data, title, num_tags=3):
    # Initialize BeautifulSoup with html data
    soup = BeautifulSoup(html_data, 'html.parser')
    
    # Extract text from HTML excluding any script or style tags
    text = " ".join([s for s in soup.strings if s.parent.name not in ['script', 'style']])
    
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Filter out non-alphanumeric tokens and stopwords
    words = [word.lower() for word in tokens if word.isalnum() and word.lower() not in stopwords.words('english')]
    
    # Filter out words that are shorter than 2 characters
    words = [word for word in words if len(word) > 1]
    
    # Initialize a frequency distribution
    fdist = FreqDist(words)
    
    # Get the most common words excluding words that contain digits
    common_words = [word for word in fdist.most_common() if not any(char.isdigit() for char in word[0])]
    
    # Remove title words from common_words
    title_words = re.findall(r'\b\w+\b', title.lower())
    common_words = [word for word in common_words if word[0] not in title_words]
    
    # Get top tags
    top_tags = [tag[0] for tag in common_words[:num_tags]]
    
    return top_tags

# Starting URL and depth of crawling
start_url = ["http://www.microsoft.com", "http://www.apple.com", "http://www.nintendo.com", "http://www.google.com", "http://www.yahoo.com", "http://www.w3.org", "http://www.mozilla.org", "http://www.geocities.org", "http://www.myspace.com", "http://www.archlinux.org", "http://www.kernel.org", "http://www.debian.org", "http://www.lkml.org", "http://www.freebsd.org", "http://www.openbsd.org", "http://www.netbsd.org", "http://www.idsoftware.com", "http://www.ask.com", "http://www.gnu.org", "http://www.linux.org", "http://en.wikipedia.org", "http://www.xbox.com"]
crawling_depth = 9000

try:
    # Start crawling in a separate thread
    for url in start_url:
        thread = threading.Thread(target=crawl, args=(url, crawling_depth))
        thread.start()

    # Wait for the crawling thread to finish
    while not stopCrawling:
        time.sleep(10)
        print("Saving data...")
        start = time.time()
        localData = globalData # Make a copy so we are not infinitly copying data into db

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS GlobalData''')
        # Create a table to store the data
        cursor.execute('''CREATE TABLE IF NOT EXISTS GlobalData (
                            id INTEGER PRIMARY KEY,
                            url TEXT,
                            title TEXT,
                            tags TEXT)''')

        # Insert data into the table
        for data_dict in globalData:
            url = data_dict.get("url")
            title = data_dict.get("title")
            tags = ", ".join(data_dict.get("tags"))  # Join the tags list into a comma-separated string
            cursor.execute("INSERT INTO GlobalData (url, title, tags) VALUES (?, ?, ?)", (url, title, tags))

        # Commit changes and close connection
        conn.commit()
        conn.close()
        end = time.time()
        print(f"{ len(globalData )} entries saved in { end - start } seconds.")
    print("Crawling finished. JSON data written to output.json.")
except KeyboardInterrupt:
    exit()