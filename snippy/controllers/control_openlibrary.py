import time
import asyncio

from typing import Dict

from ..file import FileManager
from ..scrapers import OpenLibrary


class OpenLibraryController:
    """ Control center for Snippy's ocean of pdf safety checks. """

    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.target = OpenLibrary(self.file_manager)


    def validate_openlibrary(self, agent: Dict[str, str | Dict[str, str]], headless: bool = True, total_books: int = 50, total_subject: int = 200) -> None:
        """ Scrapes ocean of pdf, it will take longer time """

        if not isinstance(headless, bool):
            raise ValueError("[ Snippy ] Headless must be a boolean")

        if not isinstance(agent, dict):
            raise ValueError("[ Snippy ] Agent must be a dictionary containing 'user_agent' and 'headers'.")

        if "user_agent" not in agent or "headers" not in agent:
            raise KeyError("[ Snippy ] Agent dictionary must include both 'user_agent' and 'headers' keys.")
        
        closed_category: str = "snippy/cache/closed_category_links/openlibrary.json"

        open_category: str = "snippy/cache/open_category_links/openlibrary.json"
        open_category_book: str = "snippy/cache/open_category_links/openlibrary_books.json"

        if self.file_manager.is_file_exist(closed_category) and self.file_manager.is_file_exist(open_category) and self.file_manager.is_file_exist(open_category_book):
            block_list: Dict = self.file_manager.load_json(closed_category)
            open_list: Dict = self.file_manager.load_json(open_category)
            open_book_list: Dict = self.file_manager.load_json(open_category_book)

        self.target.setup(block_list, open_list, open_book_list, book_limit = total_books, subject_limit = total_subject)

        existing_genre_data: Dict = asyncio.run(self.target.scrape(agent, headless))

        return existing_genre_data


if __name__ == "__main__":
    controller = OpenLibraryController(None)