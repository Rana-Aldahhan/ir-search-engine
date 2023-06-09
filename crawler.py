import re
import requests
from http.client import RemoteDisconnected
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def expand_document_with_crawled_data(doc_content: str) -> str:
    """
    This method takes a document content string as input and returns an updated document content string with crawled data from any URLs present in the input document content.

    The method first extracts URLs from the input document content using the __extractURLs function.
    If there are any URLs present, it crawls the text from each URL using the __crawl function and appends the crawled text to the input document content.
    Finally, it returns the updated document content with the crawled data included.

   Args:
        doc_content: The input document content string.
   Returns:
        The updated document content string with crawled data included.
    """
    document_included_urls = __extractURLs(doc_content)
    if len(document_included_urls) > 0:
        for url in document_included_urls:
            crawled_text = __crawl(url)
            doc_content += crawled_text
    return doc_content


def __extractURLs(content):
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    return urls


# def contains_invalid_extensions(url):
#     # array of frequent file response types
#     invalid_extensions = ['.exe', '.mkv', '.dmg', '.pdf', '.zip', '.gz', '.xz', '.bz2', '.png', '.jpg', '.gif', '.ico',
#                           '.re', '.crl']
#     try:
#         resource = urlparse(url).path
#         if any(suffix in resource for suffix in invalid_extensions):
#             return True
#         else:
#             return False
#     except Exception as e:
#         print(f'An error occurred in parsing {url}: {e}', file=sys.stderr)
#         return True
#
#
# def is_not_downloadable_content_response(url):
#     try:
#         response = requests.get(url, stream=True)
#         # download the first 1024 bytes of the response
#         content = response.raw.read(1024)
#
#         # check if the content looks like text or binary data
#         if all(32 <= c < 127 or c in (9, 10, 13) for c in content):
#             return True
#         else:
#             return False
#     except Exception as e:
#         print(f'An error occurred in {url}')
#         return False


def __is_text_url(url):
    # send a HEAD request to the URL to retrieve the headers
    response = requests.head(url)

    # check the Content-Type and Content-Disposition headers
    content_type = response.headers['Content-Type']
    content_disposition = response.headers.get('Content-Disposition', '')
    if 'text' in content_type and 'attachment' not in content_disposition:
        # check the file extension of the URL
        resource = urlparse(url).path
        file_extension = resource.split('.')[-1]
        # array of common text files extensions
        text_file_extensions = ['txt', 'html', 'htm', 'xml', 'csv', 'json', 'md', 'rst', 'php', 'asp', 'aspx', 'css',
                                'js', 'py', 'rb', 'java', 'c', 'cpp', 'h', 'sh', 'bat', 'log', 'ini', 'conf', 'yml',
                                'yaml']
        if file_extension in text_file_extensions:
            return True

        # download a small portion of the response and check its contents
        response = requests.get(url, stream=True)
        content = response.raw.read(1024)
        if all(32 <= c < 127 or c in (9, 10, 13) for c in content):
            return True

    return False


def __crawl(url):
    try:
        if __is_text_url(url):
            print(f"crawling {url}")
            html = urlopen(url).read()
            soup = BeautifulSoup(html, features="html.parser")

            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()  # rip it out

            # get text
            text = soup.get_text()

            # ###### some text processing #######
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
        else:
            return ''
    except (HTTPError, URLError, RemoteDisconnected) as e:
        return ''
    except Exception as e:
        return ''


__all__ = ['expand_document_with_crawled_data']
