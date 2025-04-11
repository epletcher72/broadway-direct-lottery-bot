import asyncio
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def save_auth_session(p):
    browser = await p.chromium.launch(headless=False)
    context = await browser.new_context()

    page = await context.new_page()
    await page.goto("https://lottery.broadwaydirect.com/")

    print("Please manually pass the 'Verifying you are human' page...")
    print("Waiting 20 seconds before saving session...")
    await page.wait_for_timeout(20000)  # Give you time to pass verification manually

    await context.storage_state(path="auth.json")
    print("Session saved to auth.json!")
    return context

async def is_lottery_open(page, url):
    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state('domcontentloaded')
        await stealth_async(page)

        html = await page.content()
        print(html)

        # Check for the "Enter Now" button
        enter_button = await page.query_selector('a.enter-lottery-link')
        print(enter_button)
        if enter_button:
            form_url = await enter_button.get_attribute('href')
            return form_url  # return the form URL instead of just True
        else:
            return None

    except Exception as e:
        print(f"Error checking {url}: {e}")
        return None

async def main():
    # Load users and shows
    with open("users.json") as f:
        users = json.load(f)

    with open("shows.json") as f:
        shows = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        context = await save_auth_session(p)
        # try:
        #     context = await browser.new_context(storage_state="auth.json")
        # except:
        #     print("No saved session found. Running save_auth_session() first.")
        #     context = await save_auth_session(p)

        for show in shows:
            page = await context.new_page()
            print(f"Checking: {show['name']}...")

            form_url = await is_lottery_open(page, show['url'])

            if form_url:
                print(f"{show['name']} Lottery is OPEN! Form link: {form_url}")
            else:
                print(f"{show['name']} lottery is CLOSED.")

            await page.close()

        await browser.close()




if __name__ == "__main__":
    asyncio.run(main())