import asyncio
from playwright.async_api import async_playwright, Playwright, Page, Browser
from csv import DictWriter

async def accept_Cookies(page: Page):
    try:
        await page.get_by_role('button', name='Allow all').click(timeout=2000)
    except:
        pass


async def scroll_down(page: Page):
    initial_height = 0
    print('initial height: ',initial_height)
    while True:
        current_height = await page.evaluate('document.body.scrollHeight')
        print('current height: ',current_height)
        if initial_height == current_height:
            break

        initial_height = current_height

        await page.evaluate('''
                                        
            window.scrollTo(
                0,
                document.body.scrollHeight - 600
            )
                                        ''')
        await asyncio.sleep(4)


async def load_more_page(page: Page):
    try:
        await page.wait_for_selector('text=Load More')
        await page.get_by_role('button', name='Load More').click()
    except:
        pass

async def data_extraction(page: Page, browser: Browser):
    await page.wait_for_selector("//div[contains(@class, 'card--property-wide')]//a[@href]")
    loc = page.locator("//div[contains(@class, 'card--property-wide')]//a[@href]")
    card_urls = await loc.evaluate_all('els => els.map(el => el.href)')

    CONTEXT_POOL_SIZE = 10
    context_pool = asyncio.Queue()

    for _ in range(CONTEXT_POOL_SIZE):
        ctx = await browser.new_context()
        await context_pool.put(ctx)

    semaphore = asyncio.Semaphore(10)

    print(len(card_urls), card_urls)
    async def data_from_url(url: str):
        async with semaphore:
            context = await context_pool.get()
            page = await context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=10000)
            await accept_Cookies(page)
            title = await page.get_by_role('heading', level=1, ).inner_text()
            facilities = await page.locator("//div[contains(@class, 'property__facilities__loop')]//p[contains(@class,'mt-1')]").all_inner_texts()
            data = {
                'Title':title,
                'Facilities':facilities,
                'Page':url
            }
            await page.close()
            await context_pool.put(context)
            return data


    tasks = [asyncio.create_task(data_from_url(card)) for card in card_urls]
    results = await asyncio.gather(*tasks)
    with open('GrAccommodation.csv', 'w', newline='', encoding='utf-8') as f:
        writer = DictWriter(f, fieldnames=[ 'Title','Facilities','Page'])
        writer.writeheader()
        writer.writerows(results)
    return results


async def run(playwright: Playwright):
    chromium = playwright.chromium # or "firefox" or "webkit".
    browser = await chromium.launch(headless=False)
    page = await browser.new_page()
    url = 'https://www.groupaccommodation.com/features/hen-party-houses?pageNumber=1'
    await page.goto(url, wait_until='domcontentloaded', timeout=10000)
    print(await page.title())
    await accept_Cookies(page)
    await scroll_down(page)
    print(await data_extraction(page, browser=browser))
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())