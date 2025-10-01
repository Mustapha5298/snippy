import time
import random
import asyncio

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Literal

from playwright_stealth import Stealth
from playwright.async_api import async_playwright, Page, BrowserContext, Locator, TimeoutError

from ..file import FileManager


class BarnesNobles:
    """ """
    def __init__(self, file_manager: FileManager):
        self.target_link = "https://www.barnesandnoble.com/"

        self.file_manager = file_manager
        self.helper = BarnesNobleshelper(self.file_manager)

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


    async def scrape(self, agent: Dict[str, str | Dict[str, str]], headless: bool) -> None:
        async with Stealth().use_async(async_playwright()) as p:
            browser = await p.chromium.launch(headless=headless)

            # Apply Snippy's custom user agent
            context = await browser.new_context(
                user_agent=agent["user_agent"],
                extra_http_headers=agent["headers"]
            )

            # * MAIN GRAB'S SUBJECT, BOOK LINKS
            book_links: List = await self.scrape_links(browser_context = context)

            # * MAIN GRAB'S BOOK DATA'S OR METADATA'S
            book_datas: List = await self.scrape_book_data(book_links, browser_context = context)

            await context.close()
            await browser.close()

            return book_datas


    async def scrape_links(self) -> None:
        pass


    async def scrape_book_data(self) -> None:
        pass


class BarnesNobleshelper:
    """ """
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager

    
    async def grab_subject_links(self) -> List:
        """ Scrapes entire subject links within the page range or area """
        pass


    async def grab_book_links(self) -> List:
        """ Scrapes entire book links within the page range or area """
        pass
    

    async def grab_book_data(self) -> Dict:
        """ Scrape entire book preview page range or area """
        pass