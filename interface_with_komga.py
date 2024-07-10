import importlib.util
import os
from typing import List

from dotenv import load_dotenv
from httpx import BasicAuth

import komga_api_client as komga_client
import komga_api_client.api.library_controller.get_all_2 as get_libraries
import komga_api_client.api.book_controller.get_all_books as find_book

from komga_api_client.models import LibraryDto, BookDto

load_dotenv()

client = komga_client.Client(base_url=os.getenv("KOMGA_HOST"),
                             httpx_args={
                                 'auth': BasicAuth(os.getenv('KOMGA_USER'), os.getenv('KOMGA_PASS'))
                             }
                             )
library_list: List["LibraryDto"] = get_libraries.sync(client=client)

correct_library_path = "/mnt/Storage/Comics_Library"
correct_library_id = None
for library in library_list:
    if library.root == correct_library_path:
        correct_library_id = correct_library_path
if correct_library_id is None:
    print("Could not find library")
    exit()

book_to_find = "2000AD 2352 (2023) (Digital-Empire)"  # Don't use extension.
book_options = find_book.sync(client=client, search=book_to_find)