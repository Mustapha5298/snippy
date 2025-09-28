import time
import random
import asyncio

from pathlib import Path
from datetime import datetime
from typing import Dict, List

from playwright_stealth import Stealth
from playwright.async_api import async_playwright, Page, BrowserContext

from ..file import FileManager


class OpenLibrary:
    """ Scraping book's on official ocean of pdf website """

    def __init__(self, file_manager: FileManager):
        self.target_link = "https://openlibrary.org"

        self.file_manager = file_manager
        self.helper = OpenLibraryHelper(self, self.file_manager)

        self.test_path = Path("snippy/scrapers/test.txt").read_text(encoding = 'utf-8')

        self.closed_category: Dict = None
        self.open_category: Dict = None
        self.open_category_book: Dict = None
        
        self.subject_limit: int = 200
        self.book_limit: int = 30

        self.tabs = 3


    def setup(self, block_list: Dict, open_list: Dict, open_book_list, book_limit: int = 50, subject_limit: int = 50) -> List:
        """ Setup class attrbiutes """
        self.closed_category = block_list
        self.open_category = open_list
        self.open_category_book = open_book_list

        self.subject_limit = subject_limit
        self.book_limit = book_limit


    async def scrape(self, agent: Dict[str, str | Dict[str, str]], headless: bool) -> Dict:
        """ Scrape books online on Open Library Website """
        async with Stealth().use_async(async_playwright()) as p:
            browser = await p.chromium.launch(headless=headless)

            # Apply Snippy's custom user agent
            context = await browser.new_context(
                user_agent=agent["user_agent"],
                extra_http_headers=agent["headers"]
            )

            # * GRABS SUBJECT, BOOK LINKS
            book_links: List = await self.scrape_links(browser_context = context)

            book_datas: List = await self.scrape_book_data(book_links, browser_context = BrowserContext)

            await context.close()
            await browser.close()

            return book_datas


    async def scrape_links(self, browser_context: BrowserContext) -> List:
        """ Scrape ocean of pdf's genre """
        # * Scrape only subject page of openlibrary
        if len(self.open_category["subjects"]) == 0:

            # * GRABS SUBJECT LINKS AS A STARTER
            page = await browser_context.new_page()
            await self.helper.grab_subject_links(page, goto_link = f"{self.parent.target_link}/subjects/")
            page.close()

        # * GRABS SUBJECT'S BOOK LINKS
        subject_links = [s["subject_link"] for s in self.open_category["subjects"][:self.tabs]]

        tasks = [self.helper.grab_book_links(await browser_context.new_page(), goto_link=link) for link in subject_links]

        await asyncio.gather(*tasks)

        return self.open_category_book["books"]
        

    async def scrape_book_data(self, book_links: List, browser_context: BrowserContext) -> None:
        """ Gets Book Data """
        return book_links



class OpenLibraryHelper:
    """ Helper class which contains the scraping content """
    def __init__(self,parent: OpenLibrary,  file_manager: FileManager):
        self.parent = parent
        self.file_manager = file_manager

        self.test_path = Path("snippy/scrapers/test.txt").read_text(encoding = 'utf-8')


    async def normalize_subject_link(self,text: str, href: str) -> str:
        """ Best for avoiding /search links or href's """
        if href.startswith("/subjects/"):
            return f"https://openlibrary.org{href}"
        
        elif href.startswith("/search"):
            slug = text.strip().lower().replace(" ", "_")
            return f"https://openlibrary.org/subjects/{slug}"
        
        return None


    async def grab_subject_links(self, page: Page, goto_link: str = None) -> None:
        """ Grabs subject header links or also known genre's too. """
        # page.set_content(self.parent.test_path)

        if len(self.parent.open_category["subjects"]) >= self.parent.subject_limit:
            print("[ Snippy ] Subject limit reached.")
            return

        if goto_link:
            await page.goto(goto_link)

        block_list: Dict = self.parent.closed_category
        open_list: Dict = self.parent.open_category

        new_data: int = 0

        links = page.locator('a[href*="/subjects/"], a[href*="/search"][href*="subject%3A"]')
        count: int = await links.count()

        for i in range(count):
            link = links.nth(i)
            text: str = (await link.inner_text()).strip()
            href: str = await link.get_attribute("href")

            normalized_href: str = await self.normalize_subject_link(text = text, href = href)

            if normalized_href:
                subject_data: Dict = {
                    "subject_name": text,
                    "subject_link": normalized_href
                }

                if subject_data not in open_list["subjects"] and subject_data not in block_list["subjects"] and len(open_list["subjects"]) != self.parent.subject_limit:
                    open_list["subjects"].append(subject_data)
                    new_data += 1

        open_list["total_subjects"] = len(open_list["subjects"])
        open_list["date_updated"] = datetime.today().strftime('%Y-%m-%d')

        self.file_manager.save_json("snippy/cache/open_category_links/openlibrary.json", open_list)

        self.parent.open_category = open_list

        print(f"[ Snippy ] New data added: {new_data}")


    async def grab_book_links(self, page: Page, goto_link: str, max_clicks: int = 10) -> None:
        """ Scrape book links for caching """
        if self.parent.open_category_book["total_book_scraped"] >= self.parent.book_limit:
            print("[ Snippy ] Book Link Limit Reached. ")
            return

        time.sleep(10)

        await page.goto(goto_link)

        await self.grab_subject_links(page)

        book_cards = page.locator('a[href^="/books/"]')
        next_btn = page.locator('button.slick-next')

        clicks = 0

        new_data = 0

        while True:
            hrefs = await book_cards.evaluate_all("els => els.map(e => e.getAttribute('href'))")
            for href in hrefs:
                data: Dict = {
                    "book_link": f"https://openlibrary.org{href}",
                    "is_scraped": False
                }

                if data not in self.parent.open_category_book["books"] and len(self.parent.open_category_book["books"]) != self.parent.book_limit:
                    self.parent.open_category_book["books"].append(data)
                    new_data += 1

            disabled = await next_btn.get_attribute("aria-disabled")
            disabled = (disabled or "").lower()

            if disabled == "true" or clicks >= max_clicks or len(self.parent.open_category_book["books"]) >= self.parent.book_limit:
                print("[ Snippy ] Scraping book link stopped")
                break

            await next_btn.click()
            await page.wait_for_timeout(random.choice([1000, 500, 1500]))

            clicks += 1
            # print(clicks)

        if new_data:
            print("[ Snippy ] New Book Link Data Added: ", new_data)
        else:
            print("[ Snippy ] No Book Added")

        self.parent.open_category_book["date_updated"] = datetime.today().strftime('%Y-%m-%d')
        self.parent.open_category_book["total_book_scraped"] = sum(1 for book in self.parent.open_category_book["books"] if book.get("is_scraped") is False)
        self.parent.open_category_book["total_book_links"] = len(self.parent.open_category_book["books"])

        self.file_manager.save_json("snippy/cache/open_category_links/openlibrary_books.json", self.parent.open_category_book)

        await page.close()
        return self.parent.open_category_book["books"]


if __name__ == "__main__":
    ocean = OpenLibrary(None)
    
    ocean.scrape_links(
            agent={
                "user_agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
                "headers": {
                    "From": "https://github.com/Vince9090",
                    "X-Snippy-Bot": "SnippyBot/1.0 (contact: seeksnippy@gmail.com)",
                    "X-Snippy-Purpose": "Student project for making search engine about books; credits will be given."
                }
            },
            headless=True
        )
    
    """
    Respect Site robots.txt

    User-agent: *
    Disallow: /api
    Disallow: /edit
    Disallow: /account
    Disallow: /merges
    Disallow: /search
    Disallow: /search/publishers
    Disallow: /search/authors
    Disallow: /search/inside
    Disallow: /search/subjects
    Disallow: /search/lists
    Disallow: /advancedsearch
    Disallow: /publishers
    Disallow: /books/add
    Disallow: /qrcode
    Disallow: */borrow*
    Disallow: /*.rdf$

    Sitemap: https://openlibrary.org/static/sitemaps/siteindex.xml.gz

    User-agent: Baiduspider
    Crawl-delay: 10

    User-agent: Googlebot
    Disallow: /*.rdf$
    Crawl-delay: 10

    User-agent: AhrefsBot
    Crawl-delay: 10

    User-agent: meta-externalagent
    Crawl-delay: 10

    User-agent: anthropic-ai
    Crawl-delay: 10

    User-agent: ClaudeBot
    Crawl-delay: 10

    User-agent: openai
    Crawl-delay: 10

    User-agent: ChatGPT
    Crawl-delay: 10

    User-agent: bingbot
    Crawl-delay: 10

    User-agent: Yandex
    Crawl-delay: 10

    User-agent: *bot
    Crawl-delay: 10
    """