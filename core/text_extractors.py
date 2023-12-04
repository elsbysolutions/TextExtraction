import os
import io
import re
import requests
from typing import Union
from bs4 import BeautifulSoup
from docx import Document
from PyPDF2 import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import validators


def extract_text_from_url(url: str) -> str:
    """
    Extracts text from a given URL. 
    Currently supports PDF and HTML content types.
    
    :param url: URL of the document to be processed.
    :return: Extracted text from the document.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    content_type = response.headers.get('Content-Type', '').lower()
    
    if 'application/pdf' in content_type:
        return extract_text_from_pdf(io.BytesIO(response.content))
    elif 'text/html' in content_type:
        return extract_text_from_html(response.text)
    else:
        return "Unsupported URL content type\n"


def extract_text_from_local_file(file_path: str) -> str:
    """
    Extracts text from a local file. 
    Supported file types are PDF, DOCX, CSV, TXT, and HTML.
    
    :param file_path: Path to the local file.
    :return: Extracted text from the file.
    """
    _, file_extension = os.path.splitext(file_path)
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension in ['.csv', '.txt']:
        return extract_text_from_text_file(file_path)
    elif file_extension == '.html':
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return extract_text_from_html(html_content)
    else:
        return "Unsupported local file type\n"



def extract_text_from_pdf(file_path_or_buffer) -> str:
    """
    Extracts text from a PDF file.
    
    :param file_path_or_buffer: Path to the PDF file or a BytesIO buffer.
    :return: Extracted text from the PDF.
    """
    text = ""
    pdf_reader = PdfReader(file_path_or_buffer)
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file.
    
    :param file_path: Path to the DOCX file.
    :return: Extracted text from the DOCX.
    """
    text = ""
    doc = Document(file_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_text_from_text_file(file_path: str) -> str:
    """
    Extracts text from a text file (CSV or TXT).
    
    :param file_path: Path to the text file.
    :return: Extracted text from the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_text_from_html(html_content: str) -> str:
    """
    Extracts text from an HTML document.
    
    :param html_content: HTML content as a string.
    :return: Extracted text from the HTML.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.get_text(separator="\n", strip=True)


def extract_transcript_from_youtube_url(url):
    
    def extract_video_id_from_url(url):
        video_id_pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
        match = re.search(video_id_pattern, url)
        if match:
            return match.group(1)
        return None
    
    try:
        # Fetch the video id from the url
        video_id = extract_video_id_from_url(url)
        
        if not video_id:
            raise ValueError("No valid YouTube video ID found in the URL.")

        # Fetching the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Initialize the formatter
        formatter = TextFormatter()

        # Format the transcript into plain text
        plain_text_transcript = formatter.format_transcript(transcript)

        return plain_text_transcript
    except Exception as e:
        print("An error occurred:", e)
        return e
    

def determine_input_type(input_source: str) -> str:
    """
    Determines the type of the input source.

    :param input_source: The source from which to determine the type.
    :return: Type of the input source ('url', 'local_file', 'youtube', 'unknown').
    """
    # Check if input is a valid URL
    if validators.url(input_source):
        # Check if it is a YouTube URL
        if 'youtube.com' in input_source or 'youtu.be' in input_source:
            return 'youtube'
        else:
            return 'url'
    
    # Check for local file with file extension
    elif os.path.isfile(input_source):
        _, ext = os.path.splitext(input_source)
        if ext in ['.pdf', '.docx', '.txt', '.csv', '.html']:
            return 'local_file'

    return 'unknown'

def extract_text(input_source: str) -> str:
    """
    Automatically extracts text from various input types such as URLs, local files, or YouTube URLs.

    :param input_source: The source from which to extract text.
    :return: Extracted text from the input source or an error message if the input type is unknown.
    """
    try:
        input_type = determine_input_type(input_source)

        if input_type == 'url':
            return extract_text_from_url(input_source)
        elif input_type == 'local_file':
            return extract_text_from_local_file(input_source)
        elif input_type == 'youtube':
            return extract_transcript_from_youtube_url(input_source)
        else:
            return "Unsupported or unknown input type\n"

    except Exception as e:
        print(f"An error occurred while extracting text: {e}")
        return None

