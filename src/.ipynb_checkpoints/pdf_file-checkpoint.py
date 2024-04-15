import fitz
import re
from utils import replace_acronyms
from utils import replace_and_remove_newline
from utils import write_to_txt

class Part:
    def __init__(self, title, page_num):
        """
        Initialize a Part object with its title and page number.

        Args:
        - title (str): The title of the part.
        - page_num (int): The page number where the part starts.
        """
        self.title = title
        self.page_num = page_num
        self.bookmarks = None

    def __str__(self):
        """
        Return a string representation of the Part object.

        Returns:
        - str: A string containing the title and page number of the part.
        """
        return f"{self.title} - Page_num: {self.page_num}"


class PdfFile:
    def __init__(self, file_path):
        """
        Initialize a PdfFile object with the file path.

        Args:
        - file_path (str): The path to the PDF file.
        """
        self.doc = fitz.open(file_path)
        self.title_to_content = {
            "SECTION": "\n+++++\n",
            "PART": "\n++++\n",
            "CHAPTER": "\n+++\n",
        }
    def get_content_by_chapters_page(self):
        bookmarks = self.get_bookmarks()

        chapters = []

        for i in range(len(bookmarks) - 1):
    
            bookmark_content = ""

            bookmark = bookmarks[i]

            bookmark_content = []

            for j in range(bookmark.page_num + 1, bookmarks[i + 1].page_num):
                paras = self.get_paragraphs(page_idx=j)

                page_content = ""

                for para in paras:

                    if "References" in para:
                        break

                    page_content += para

                bookmark_content.append(
                    {"page_num": j, "content": replace_and_remove_newline(page_content)}
                )

                if self.doc[j].search_for("\nReferences\n"):
                    break

            chapters.append(
                {
                    "title": bookmark.title,
                    "content": bookmark_content,
                }
            )
        return chapters
    def get_equivalent_content_part(self, current_part, keyword):
        part = current_part
        while part is not None:
            if keyword in part.title:
                return part
            part = part.next

        part = current_part
        while part is not None:
            result = self.get_equivalent_content_part(part.down, keyword)
            if result is not None:
                return result
            part = part.next

        return None

    def get_bookmarks(self):
        """
        Retrieve bookmarks from a PDF document.

        Returns:
        - list: A list of Part objects representing the bookmarks.
        """
        bookmarks = []

        content_book_mark = self.get_equivalent_content_part(
            self.doc.outline, "Content"
        )
        # print(content_book_mark.page)
        # if content_book_mark is None:
        #     content_book_mark = self.get_equivalent_content_part(
        #         self.doc.outline, "Cover"
        #     )
        while True:
            if "1" in content_book_mark.title:
                break
            if "Section" in content_book_mark.title:
                break
            if "Part" in content_book_mark.title:
                break
            if "Chapter" in content_book_mark.title:
                break
            if content_book_mark is None:
                break
            content_book_mark = content_book_mark.next
        # print(self.doc[content_book_mark.page].get_text_blocks()[0][4])

        while "Index" not in content_book_mark.title:
            bookmarks.append(Part(content_book_mark.title, content_book_mark.page))
            blocks = self.doc[content_book_mark.page].get_text_blocks()
            name = ""
            for block in blocks:
                if "Chapter" in block[4]:
                    start = block[4].index("Chapter")
                    name = block[4][start : start + len("Chapter") + 3]
                    name.replace("\n", "")
                    break
            startSection = content_book_mark.down
            while startSection is not None:
                # print(name)
                if self.doc[startSection.page].search_for(name):
                    break
                bookmarks.append(Part(startSection.title, startSection.page))
                startSection = startSection.next
            content_book_mark = content_book_mark.next

        # for bookmark in bookmarks:
        #     print(bookmark.title)

        return bookmarks

    def get_paragraphs(self, page_idx):
        """
        Extract paragraphs from a page of the PDF document.

        Args:
        - page (fitz.Page): The page object from which to extract paragraphs.

        Returns:
        - list: A list of strings representing paragraphs extracted from the page.
        """
        page = self.doc[page_idx]
        paras = []

        blocks = page.get_text_blocks()[1:]
        # if len(blocks) >= 20: return paras

        for block in blocks:
            if any(
                block[4].startswith(key_word) for key_word in ["Table", "Box", "Fig"]
            ):
                break
            para_content = block[4].replace("\xa0", "")
            paras.append(para_content)
        return paras

    def get_content(self):
        chapters = self.get_content_by_chapters()
        content = ''
        for chapter in chapters:
            content += chapter
        return content

    def get_abbreviation_in_page(self, page_idx):
        """
        Retrieve abbreviations and their meanings from a specific page of the document.

        Args:
        - page_idx (int): Index of the page to extract abbreviations from.

        Returns:
        - dict: A dictionary mapping abbreviations to their meanings.
        """
        page = self.doc[page_idx]
        list_abb = {}
        blocks = page.get_text_blocks()
        for block in blocks[1:]:
            abbs = block[4].split("\n")
            for i in range(len(abbs)):
                if abbs[i].isupper():
                    list_abb[abbs[i]] = abbs[i + 1]
        return list_abb

    def get_abbreviation_in_doc(self):
        """
        Retrieve all abbreviations and their meanings from the document.

        Returns:
        - dict: A dictionary mapping abbreviations to their meanings.
        """
        abbreviation = self.doc.outline

        start_abb = -1
        end_abb = -1

        while abbreviation is not None:
            if ("Abbreviations" in abbreviation.title) or (
                "abbreviations" in abbreviation.title
            ):
                break
            abbreviation = abbreviation.next

        if abbreviation is None or start_abb == end_abb:
            start = False
            end = False
            for page in self.doc:
                exist = False
                for text_block in page.get_text_blocks():
                    if re.search(r"abbreviations", text_block[4], re.IGNORECASE):
                        if start is False:
                            start_abb = page.number
                        start = True
                        exist = True
                        break
                if exist is False:
                    if start is True:
                        end_abb = page.number - 1
                        if end_abb - start_abb == 0:
                            start = False
                        else:
                            end = True
                if end is True:
                    break
        else:
            start_abb = abbreviation.page
            end_abb = abbreviation.next.page

        # print(f"{start_abb} to {end_abb}")

        abbr_list = {}
        if start_abb == -1 or end_abb == -1 or start_abb == end_abb:
            return abbr_list
        for page in range(start_abb, end_abb):
            abbr_list.update(self.get_abbreviation_in_page(page_idx=page))

        # print(len(abbr_list))
        return abbr_list

    def get_content_by_chapters(self):
        bookmarks = self.get_bookmarks()

        chapters = []

        for i in range(len(bookmarks) - 1):
            # print(bookmarks[i].title)
            bookmark_content = ""

            bookmark = bookmarks[i]

            # for title, content_str in self.title_to_content.items():
            #     if title in bookmark.title:
            #         bookmark_content += content_str
            #         break

            bookmark_content += bookmark.title + "\n"

            for j in range(bookmark.page_num + 1, bookmarks[i + 1].page_num):
                paras = self.get_paragraphs(page_idx=j)

                for para in paras:

                    if "References" in para:
                        break

                    bookmark_content += para

                if self.doc[j].search_for("\nReferences\n"):
                    break
            # print(replace_and_remove_newline(bookmark_content))
            # bookmark_content = re.sub(r"\s+", " ", bookmark_content).strip()
            # bookmark_content = replace_acronyms(bookmark_content, dict)
            chapters.append(replace_and_remove_newline(bookmark_content))
        return chapters
