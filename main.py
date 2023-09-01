import os
from PyPDF2 import PdfReader
import argparse
import re
import requests
from xml.etree import ElementTree as ET

ARXIV_URL = "http://export.arxiv.org/api"


def extract_doi(page_text):
    # The regular expression to match a DOI
    doi_pattern = r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b"

    # Perform a case-insensitive search for the DOI pattern in the text
    match = re.search(doi_pattern, page_text, re.IGNORECASE)

    # If a match is found, return it; otherwise, return None
    if match:
        return match.group(0)
    else:
        return None


def get_arxiv_title(arxiv_id):
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    response = requests.get(url)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
            title_element = entry.find("{http://www.w3.org/2005/Atom}title")
            if title_element is not None:
                return title_element.text
    else:
        print(f"Failed to get data from arXiv API, status code: {response.status_code}")

    return None


def extract_arxiv_id(page_text):
    # The regular expression to match an arXiv ID
    arxiv_pattern = r"\b\d{4}\.\d{4,5}(v\d+)?\b"

    # Search for the arXiv ID pattern in the text
    match = re.search(arxiv_pattern, page_text)

    # If a match is found, return it; otherwise, return None
    if match:
        return match.group(0)
    else:
        return None


def sanitize_title(title):
    # Replace special characters with "_"
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)

    # Replace spaces with "_"
    safe_title = safe_title.replace(" ", "_")

    return safe_title


def get_pdf_title(pdf_path):
    # Try to read from metadata
    reader = PdfReader(pdf_path)
    meta = reader.metadata
    title = meta.title

    # If metadata does not contain title, try to extract it from text
    if not title:
        page = reader.pages[0]
        page_text = page.extract_text()

        doi = extract_doi(page_text)
        arxiv = extract_arxiv_id(page_text)

    return "testing"
    return sanitize_title(title)


def rename_pdf(old_path, new_title):
    folder = os.path.dirname(old_path)
    new_path = os.path.join(folder, new_title + ".pdf")
    os.rename(old_path, new_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename a PDF file to its title.")
    parser.add_argument(
        "--pdf_path", type=str, help="Path to the PDF file to be renamed"
    )

    args = parser.parse_args()
    pdf_path = args.pdf_path

    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"The file {pdf_path} does not exist.")
        exit(1)

    # Extract title and rename
    title = get_pdf_title(pdf_path)
    if title:
        print(f"Renaming to {title}.pdf")
        rename_pdf(pdf_path, title)
    else:
        print("Could not determine title.")
