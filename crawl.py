import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import multiprocessing
import concurrent.futures
import re

def create_directory(base_dir, sub_dir):
    sub_dir = str(sub_dir)
    path = os.path.join(base_dir, sub_dir)
    os.makedirs(path, exist_ok=True)
    return path

def download_media(url, directory):
    try:
        # Remove any fragment identifier (like #t=1)
        url = url.split('#')[0]
        
        # Ensure the URL is complete
        if not url.startswith(('http://', 'https://')):
            url = f"https://wu-massage.com/{url.lstrip('/')}"
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Extract filename, preserving the original extension
        filename = os.path.basename(urlparse(url).path)
        file_path = os.path.join(directory, filename)
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded media: {file_path}")
    except Exception as e:
        print(f"Failed to download media {url}: {e}")

def generate_keywords(download_directory, number):
    return [
        f"{download_directory}｜免房費｜編號{number:02}區",
        f"{download_directory}｜免房費｜編號#{number:02}區"
    ]

def clean_content(targeted_content):
    # Split the content into lines
    lines = targeted_content.split('\n')
    
    # Remove leading and trailing whitespace from each line
    lines = [line.strip() for line in lines]
    
    # Remove completely empty lines
    lines = [line for line in lines if line]
    
    # Rejoin the lines, preserving single newlines between non-empty lines
    cleaned_content = '\n'.join(lines)
    
    return cleaned_content


def scrape_page(base_url, number, download_directory):
    keywords = generate_keywords(download_directory, number)
    
    for target_keyword in keywords:
        page_url = f"{base_url}?keyword={target_keyword}"
        print(f"Scraping {page_url}...")
        
        try:
            response = requests.get(page_url)
            response.raise_for_status()
            page_soup = BeautifulSoup(response.text, "html.parser")

            content_spans = page_soup.find_all('span', class_='cnt more')
            
            for content_span_index, content_span in enumerate(content_spans, 1):
                links = content_span.find_all('a', href=True)
                
                matching_links = [
                    link for link in links 
                    if target_keyword in link.get('href', '') or target_keyword in link.get_text(strip=True)
                ]
                
                if matching_links:
                    sub_dir = create_directory(download_directory, f"{number}")

                    # Replace <br> tags with newline characters
                    #for br in content_span.find_all('br'):
                    #    br.replace_with('\n')
                    
                    # Get text content, preserving line breaks
                    targeted_content = content_span.get_text(strip=False)
                    
                    # Remove consecutive empty lines
                    cleaned_content = clean_content(targeted_content)
                    
                    with open(os.path.join(sub_dir, 'content.txt'), 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    
                    with open(os.path.join(sub_dir, 'links.txt'), 'w', encoding='utf-8') as f:
                        for link in matching_links:
                            href = link['href']
                            link_text = link.get_text(strip=True)
                            f.write(f"Link: {href}\nText: {link_text}\n\n")
                    
                    post_div = content_span.find_parent('div', class_='post')
                    if post_div:
                        # Look for source tags with mp4 files
                        source_tags = post_div.find_all('source', src=True)
                        
                        # Also look for video and img tags with mp4 links
                        video_tags = post_div.find_all('video', src=True)
                        img_tags = post_div.find_all('img', src=True)
                        
                        # Combine and download media
                        all_media = (
                            [tag['src'] for tag in source_tags] +
                            [tag['src'] for tag in video_tags] +
                            [tag['src'] for tag in img_tags]
                        )
                        
                        # Filter for MP4 files
                        mp4_links = [
                            link for link in all_media 
                            if link.lower().endswith('.mp4') or 
                               '/mp4/' in link.lower() or 
                               'CKEdit/images/file' in link
                        ]
                        
                        # Download unique MP4 links
                        for mp4_link in set(mp4_links):
                            download_media(mp4_link, sub_dir)
                    
                    print(f"Processed content span {content_span_index} for page {number}")
                    return  # Exit after first match

        except Exception as e:
            print(f"Failed to scrape page {number} with keyword {target_keyword}: {e}")

def main(base_url, download_directory, start_number, end_number):
    # Use ProcessPoolExecutor for CPU-bound tasks
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        # Submit all scraping tasks
        futures = [
            executor.submit(scrape_page, base_url, number, download_directory) 
            for number in range(start_number, end_number + 1)
        ]
        
        # Wait for all tasks to complete
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    base_url = "https://wu-massage.com"
    dir_list = [
        "西門定點","中山定點","三重定點","板橋定點",
        "蘆洲定點","信義定點","基隆定點","汐止定點",
    ]
    start_number = 79
    end_number = 103
    for download_directory in dir_list[0:1]:
        main(base_url, download_directory, start_number, end_number)