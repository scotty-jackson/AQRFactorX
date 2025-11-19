#!/usr/bin/env python3
"""
Download all datasets from AQR Capital Management's data library
https://www.aqr.com/Insights/Datasets
"""

import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re

def download_file(url, output_path):
    """Download a file from URL to output_path"""
    try:
        print(f"Downloading: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        # Get total size
        total_size = int(response.headers.get('content-length', 0))

        with open(output_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    downloaded += len(chunk)
                    f.write(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"  Progress: {percent:.1f}%", end='\r')

        print(f"\n  Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False

def get_dataset_links(base_url):
    """Get all dataset page links from the main page"""
    try:
        print(f"Fetching main page: {base_url}")
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all dataset links
        dataset_links = []

        # Look for links that contain dataset pages
        for link in soup.find_all('a', href=True):
            href = link['href']
            # AQR dataset pages are typically under /Insights/Datasets/
            if '/Insights/Datasets/' in href and href != '/Insights/Datasets':
                full_url = urljoin(base_url, href)
                if full_url not in dataset_links:
                    dataset_links.append(full_url)

        print(f"Found {len(dataset_links)} dataset pages")
        return dataset_links

    except Exception as e:
        print(f"Error fetching main page: {e}")
        return []

def get_download_links_from_dataset_page(dataset_url):
    """Extract download links from a specific dataset page"""
    try:
        print(f"\nProcessing: {dataset_url}")
        response = requests.get(dataset_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the dataset name from the page title or heading
        title = soup.find('h1')
        dataset_name = title.get_text(strip=True) if title else "Unknown"
        dataset_name = re.sub(r'[^\w\s-]', '', dataset_name)  # Clean filename
        dataset_name = re.sub(r'\s+', '_', dataset_name)

        print(f"  Dataset: {dataset_name}")

        downloads = []

        # Look for Excel/CSV download links
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Check if it's a data file
            if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.csv', '.zip']):
                full_url = urljoin(dataset_url, href)

                # Extract filename from URL
                filename = os.path.basename(urlparse(full_url).path)
                if not filename:
                    filename = f"{dataset_name}.xlsx"

                downloads.append({
                    'url': full_url,
                    'filename': filename,
                    'dataset_name': dataset_name
                })
                print(f"  Found file: {filename}")

        return downloads

    except Exception as e:
        print(f"  Error processing dataset page: {e}")
        return []

def main():
    base_url = "https://www.aqr.com/Insights/Datasets"
    output_dir = "/mnt/s/Projects/AQRFactorX/data/aqr_raw"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    print("="*80)
    print("AQR Data Library Downloader")
    print("="*80)

    # Get all dataset page links
    dataset_links = get_dataset_links(base_url)

    if not dataset_links:
        print("No dataset links found. The page structure may have changed.")
        return

    # Process each dataset page
    all_downloads = []
    for dataset_url in dataset_links:
        downloads = get_download_links_from_dataset_page(dataset_url)
        all_downloads.extend(downloads)
        time.sleep(1)  # Be polite to the server

    print("\n" + "="*80)
    print(f"Found {len(all_downloads)} files to download")
    print("="*80)

    # Download all files
    successful = 0
    failed = 0

    for i, item in enumerate(all_downloads, 1):
        print(f"\n[{i}/{len(all_downloads)}]")

        # Create subdirectory for each dataset
        dataset_dir = os.path.join(output_dir, item['dataset_name'])
        os.makedirs(dataset_dir, exist_ok=True)

        output_path = os.path.join(dataset_dir, item['filename'])

        # Skip if file already exists
        if os.path.exists(output_path):
            print(f"  File already exists: {output_path}")
            successful += 1
            continue

        if download_file(item['url'], output_path):
            successful += 1
        else:
            failed += 1

        time.sleep(1)  # Be polite to the server

    print("\n" + "="*80)
    print("Download Summary")
    print("="*80)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(all_downloads)}")
    print(f"\nAll files saved to: {output_dir}")

if __name__ == "__main__":
    main()
