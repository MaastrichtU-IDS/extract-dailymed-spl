import aiohttp
import asyncio
import json

BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
SPL_FOLDER = "/data/dailymed/spls/"

async def fetch_page(session, page):
    params = {
        'page': page
    }
    async with session.get(BASE_URL, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error {response.status} on page {page}")
            return None
        
async def fetch_all_spls():
    async with aiohttp.ClientSession() as session:
        # First, get the total count of SPLs to determine how many pages to fetch
        initial_data = await fetch_page(session, 1)
        total_count = initial_data['metadata']['total_elements']
        page_size = initial_data['metadata']['elements_per_page']
        total_pages = (total_count + page_size - 1) // page_size

        # Fetch all pages concurrently
        tasks = [fetch_page(session, page) for page in range(2, total_pages + 1)]
        pages = await asyncio.gather(*tasks)

        # Combine the results
        all_spls = initial_data['data']
        for page in pages:
            if page:
                all_spls.extend(page['data'])

        return all_spls

def save_spls_to_json(spls, filename):
    with open(filename, "w") as file:
        json.dump(spls, file, indent=4)

if __name__ == "__main__":
    spls = asyncio.run(fetch_all_spls())
    save_spls_to_json(spls,f"{SPL_FOLDER}/async-spls.json")

    print(f"Total SPLs fetched: {len(spls)}")


