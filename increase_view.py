import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import asyncio
import aiohttp

# List of thread URLs to simulate views for
thread_urls = [
    "https://www.jkforum.net/p/thread-14412248-1-1.html",
    "https://www.jkforum.net/p/thread-14412256-1-1.html",
    "https://www.jkforum.net/p/thread-13966857-1-1.html",
    "https://www.jkforum.net/p/thread-14403955-1-1.html",
    "https://www.jkforum.net/p/thread-13967340-1-1.html", 

]

# Number of total views per page
views_per_page = 100000

# Total progress bar setup
total_requests = len(thread_urls) * views_per_page
progress_bar = tqdm(total=total_requests, desc="Simulating Views", unit="view")


def fetch_view_count(url, session):
    """Fetch the current view count from the webpage synchronously."""
    try:
        with session.get(url) as response:
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                view_count_element = soup.select_one("span > em")  # Modify selector if necessary
                if view_count_element:
                    return int(view_count_element.text.strip())
    except Exception as e:
        print(f"Error fetching view count for {url}: {e}")
    return None


async def simulate_view(url, session):
    """Simulates a single view asynchronously."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                pass  # Successful request
    except Exception:
        pass  # Ignore errors to continue
    finally:
        progress_bar.update(1)


async def increase_views_for_pages():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in thread_urls:
            for _ in range(views_per_page):
                tasks.append(simulate_view(url, session))

        await asyncio.gather(*tasks)

    progress_bar.close()
    print("All requests have been completed.")


if __name__ == "__main__":
    # Fetch initial view counts synchronously
    print("\nFetching initial view counts...")
    with requests.Session() as sync_session:
        initial_view_counts = {}
        for url in thread_urls:
            initial_view_counts[url] = fetch_view_count(url, sync_session)
            print(f"Initial view count for {url}: {initial_view_counts[url]}")

    # Simulate views asynchronously
    asyncio.run(increase_views_for_pages())

    # Fetch final view counts synchronously
    print("\nFetching final view counts...")
    with requests.Session() as sync_session:
        for url in thread_urls:
            final_view_count = fetch_view_count(url, sync_session)
            print(f"Final view count for {url}: {final_view_count}, Difference: {final_view_count - initial_view_counts[url]}")
