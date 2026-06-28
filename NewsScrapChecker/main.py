import asyncio
from playwright.async_api import async_playwright, Playwright, Page, Browser
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
import openpyxl

complet_url ='https://www.einpresswire.com/'
base_url = 'https://www.einpresswire.com/world-media-directory/4/alabama'

all_name_url = [] # base one
news_site_details = [] # name, location, is_scrapable

async def col_1(page: Page):
    all_div = await page.locator('//div/div[contains(@class, "noarrows")]/div[1]/div/div/a').all()
    print(all_div)
    for each_div in all_div:
        l = await each_div.get_attribute('href')
        all_name_url.append(urljoin(complet_url, str(l)))
    print(all_name_url)


async def col_2(page: Page):
    all_div = await page.locator('//div/div[contains(@class, "noarrows")]/div[2]/div/div/a').all()
    print(all_div)
    for each_div in all_div:
        l = await each_div.get_attribute('href')
        all_name_url.append(urljoin(complet_url, str(l)))
    print(all_name_url)

# ------------------------------------------------------------------------------

async def scrape_fp_url(semaphore, browser, url): # for using this u have to use async gather and for url in all_front_page_url
    async with semaphore:
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Sec-CH-UA": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": '"Windows"',
                "Cache-Control": "max-age=0",
                "DNT": "1",
            })
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle")

            website_name = page.locator('//table[contains(@class, "simple")]/tbody/tr/td').first
            website_name = await website_name.text_content()

            location = await page.locator('//table[contains(@class, "simple")]//th[text()="Location"]/following-sibling::td').first.text_content()

            fp = page.locator('//tbody//tr//td//a[contains(@class, "verbatim")]').first
            fp_url = await fp.get_attribute('href')

            news_site_details.append({
                'Location': location.strip() if location else None,
                'Website': website_name.strip() if website_name else None,
                'Front_Page_URL': fp_url,
                'allow_scraping': False
            })

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            news_site_details.append({
                'Location': None,
                'Website': None,
                'allow_scraping': False,
                'Front_Page_URL': None
            })

        finally:
            await context.close()


async def check_scrapable(news_site_details: dict) -> dict:
    url = news_site_details.get('Front_Page_URL')

    if url is None:
        news_site_details['allow_scraping'] = 'No'
        return news_site_details

    try:
        rp = RobotFileParser()
        rp.set_url(urljoin(url, '/robots.txt'))
        await asyncio.to_thread(rp.read)
        news_site_details['allow_scraping'] = 'Yes' if rp.can_fetch('*', url) else 'No'
    except:
        news_site_details['allow_scraping'] = 'Yes'

    return news_site_details


def save_to_excel(news_site_details: list):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "News Sites"

    # Header row
    ws.append(['Location', 'Website', 'Allow Scraping'])

    # Data rows
    for site in news_site_details:
        ws.append([
            site.get('Location'),
            site.get('Website'),
            site.get('allow_scraping')
        ])

    wb.save('news_sites.xlsx')
    print("Excel file saved!")


async def run(playwright: Playwright):
    chromium = playwright.chromium # or "firefox" or "webkit".
    browser = await chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(base_url)

    await col_1(page)
    await col_2(page)

    semaphore = asyncio.Semaphore(3)
    await asyncio.gather(*[scrape_fp_url(semaphore, browser, url) for url in all_name_url])

    # Check does site allow to scrap or not
    await asyncio.gather(*[check_scrapable(site) for site in news_site_details])
    save_to_excel(news_site_details)

    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())