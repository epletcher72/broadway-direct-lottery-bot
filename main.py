import asyncio
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async


async def is_lottery_open(page, url):
    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state('domcontentloaded')

        # Use stealth
        await stealth_async(page)

        # Try to detect form field (e.g., name input)
        name_input = await page.query_selector('input[name="name"]')
        return name_input is not None

    except Exception as e:
        print(f"Error checking {url}: {e}")
        return False


async def main():
    # Load users and shows
    with open("users.json") as f:
        users = json.load(f)

    with open("shows.json") as f:
        shows = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True later
        context = await browser.new_context()

        for show in shows:
            page = await context.new_page()
            print(f"Checking: {show['name']}...")

            open_status = await is_lottery_open(page, show['url'])

            if open_status:
                print(f" {show['name']} lottery is OPEN!")
            else:
                print(f" {show['name']} lottery is CLOSED.")

            await page.close()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())