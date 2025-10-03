import time
import asyncio

from typing import Dict, List, Literal

from ..file import FileManager
from ..scrapers import BarnesNobles

class BarnesNoblesController:
    """ Control center for Snippy's ocean of pdf safety checks. """

    def __init__(self, file_manager: FileManager) -> None:
        self.file_manager = file_manager

        self.target = BarnesNobles(self.file_manager)


    def validate_barnesnobles(self, agent: Dict[str, str | Dict[str, str]], type: List | Literal["--subject_list_links", "--book_list_links",  "--book_data"] = "--all", headless: bool = True, total_books: int = 50, total_subject: int = 200, specific_link: List | str = None) -> None:
        """ Scrapes ocean of pdf, it will take longer time """

        if not isinstance(headless, bool):
            raise ValueError("[ Snippy ] Headless must be a boolean")

        if not isinstance(agent, dict):
            raise ValueError("[ Snippy ] Agent must be a dictionary containing 'user_agent' and 'headers'.")

        if "user_agent" not in agent or "headers" not in agent:
            raise KeyError("[ Snippy ] Agent dictionary must include both 'user_agent' and 'headers' keys.")
        
        if specific_link and len(specific_link) == 0 and "--all" not in type:
            raise ValueError("[ Snippy ] Specific link needs a value, not empty or None")
        
        closed_category: str = "snippy/cache/barnesnobles/closed_category_links/barnesnobles.json"

        open_category: str = "snippy/cache/barnesnobles/open_category_links/barnesnobles.json"
        open_category_book: str = "snippy/cache/barnesnobles/open_category_links/barnesnobles_books.json"

        shelf_data_path: str = "snippy/data/barnesnobles_shelf/shelf.json"
        book_data_path: str = "snippy/data/barnesnobles_shelf/book.json"
        book_author_data_path: str = "snippy/data/barnesnobles_shelf/author.json"
        book_publisher_data_path: str = "snippy/data/barnesnobles_shelf/publisher.json"
        book_categories_data_path: str = "snippy/data/barnesnobles_shelf/categories.json"

        if self.file_manager.is_file_exist(closed_category) and self.file_manager.is_file_exist(open_category) and self.file_manager.is_file_exist(open_category_book):
            block_list: Dict = self.file_manager.load_json(closed_category)
            open_list: Dict = self.file_manager.load_json(open_category)
            open_book_list: Dict = self.file_manager.load_json(open_category_book)

            book_shelf_data_list = self.file_manager.load_json(shelf_data_path)

            book_data_list = self.file_manager.load_json(book_data_path)
            book_author_data_list = self.file_manager.load_json(book_author_data_path)
            book_publisher_data_list = self.file_manager.load_json(book_publisher_data_path)
            book_categories_data_list = self.file_manager.load_json(book_categories_data_path)
            

        self.target.setup(block_list, open_list, open_book_list, book_data_list, book_publisher_data_list, book_categories_data_list, book_author_data_list, book_shelf_data_list, book_limit = total_books, subject_limit = total_subject, scrape_type = type, links = specific_link)

        existing_genre_data: Dict = asyncio.run(self.target.scrape(agent, headless))

        return existing_genre_data


if __name__ == "__main__":
    pass