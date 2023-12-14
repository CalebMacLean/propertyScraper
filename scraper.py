# Imports
from requests_html import HTMLSession
from bs4 import BeautifulSoup, SoupStrainer, element
from requests.exceptions import Timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

# The starting pairid = parid=00102000
# Current Pages URL
curr_url = 'https://www.washoecounty.gov/assessor/cama/?parid=00102008'

# HTMLSessiException from extract data : Connection is closedon obj variable used in rendering pages
session = HTMLSession()

# Parsing Functions

def fetch_rendered_html(url):
    """
    Fetches and renders HTML document for a given url and returns a new HTML document with updated data.

    Parameters:
    - url (str) : URL of dynamically updated page.

    Return:
    - HTML: The rendered HTML document.
    """
    # Uses HTMLSession object and sends a GET response to the url
    response = session.get(url)
    # Raises an HTTPError for bad response
    response.raise_for_status()
    # Uses HTML Session object to render the html in a headless browser, updating the template language into usable values
    response.html.render(sleep = 4, keep_page = True, scrolldown = 1, timeout = 20)
    # Returns HTML Document with updated data
    return response.html.html


def render_page_with_retry(url, max_retries=20):
    """
    Retries fetching and rendering HTML document in case of Timeout Exceptions.

    Parameters:
    - url (str) : URL of dynamically updated page.
    - max_retries (int) : The number of times that fetch_rendered_html() should be retried.

    Return:
    - HTML: The rendered HTML document
    """
    # retries Var tracks the attempt the function is on.
    retries = 0
    # While loop modified by optional parameter max_retries.
    while retries < max_retries:
        try:
            return fetch_rendered_html(url)
        # Exception looking for Timeout Errors. Prints which attempt we are on and updates retries Var.
        except TimeoutError:
            print(f"TimeoutError: Retrying ({retries + 1}/{max_retries})")
            retries += 1
    # In the case that the retry limit is reached, this exception will raise and inform of problem.
    raise TimeoutError('Max retires exceeded')


def find_owner_info_by_header(header_name, th_iterable):
        """
        Finds and returns element with relevant data by using the row's table header.

        Parameters:
        - header_name (str) : Name of a th element.
        - th_iterable (ResultSet) : BeautifulSoup ResultSet containing th elements.

        Return:
        - Element (obj) : A BeautifulSoup Element Object.
        """
        try:
            # Takes th soup iterable, and isolates one th at a time.
            for header in th_iterable:
                # Accesses the current th's contents.
                for content in header.contents:
                    # Checks that contents are a string and match the given header name.
                    if isinstance(content, element.NavigableString) and (content.string.strip().lower() == header_name.lower()):
                        # Returns the actual owner data element that is in the same row.
                        return header.next_sibling.next_sibling
                else:
                    continue
        # Error Handling
        except Exception as e:
             print(f"Exception from find_owner_info_by_header : {e}")

        # Case: Couldn't find header or owner data element.
        return None


def get_owner_data(header_name, th_iterable):
    """
    Retrieves data from a td element.

    Parameters:
    - header_name (str) : Name of a th element.
    - th_iterable (ResultSet) : BeautifulSoup ResultSet containg th elements.

    Returns:
    - Data (str) : Text of td element.
    """

    def clean_up_string(str):
        """Clean up string by removing unwanted characters."""
        cleaned_string = re.sub(r'[\xa0\n]', ' ', str)
        return re.sub(r'\s+', ' ', cleaned_string).strip()
    
    try:    
        # Case for Searching for Situs 1
        if(header_name.lower() == 'situs 1'):
            # Locates Parcel's address element.
            element = find_owner_info_by_header('situs 1', th_iterable)
            # Creates and Returns list of elements relevant strings.
            if element:
                return " ".join([clean_up_string(string) for string in element.strings])
            else:
                return None
    
        # Case for Searching for Owner
        if (header_name.lower() == 'owner 1'):
            # Locates and returns Parcel's owner's name element.
            element = find_owner_info_by_header('owner 1', th_iterable)
            if element:
                return element.string.strip()
            else:
                return None
        
        # Case for Searching for Mail Address
        if (header_name.lower() == 'mail address'):
            # Locates Parcel's owner's mail address element.
            element = find_owner_info_by_header('mail address', th_iterable)
            if element:
                # Creates list of element's relevant strings, but they are very messy and need to be cleaned up.
                result = [clean_up_string(string) for string in element.strings if clean_up_string(string) != '']
                return " ".join(result)
            else:
                return None
    
    except Exception as e:
        print(f"Exception from get_owner_data : {e}")
        

def get_sales_data(spans):
        """
        Uses Soup span iterable to locate grantor and grantee td, then uses the grantee element to locate the value td
        Returns a list of all the data [grantor, grantee, value]

        Parameters:
        - Spans (ResultSet) : BeautifulSoup ResultSet containing span elements.

        Return:
        - Data (List) : [Grantor (str), Grantee (str), Value (str)]
        """
        try:    
            # Grantor and Grantee have unique enough element and class names to identify with span iterable
            grantor = [content.string.strip() for content in spans[0].contents if content.string and content.string.strip()]
            grantee = [content.string.strip() for content in spans[1].contents if content.string and content.string.strip()]
            # Must use found Grantee td to locate value element
            # value_element = spans[1].parent.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling
            value_element = spans[1].parent
            # loop to locate value element, changed for readability
            index = 0
            while (index < 12):
                value_element = value_element.next_sibling
                index += 1
            # Actual Data for Sale Value
            value = value_element.text.strip()

            return [grantor, grantee, value]
        
        except Exception as e :
            print(f"Exception from get_sales_data : {e}")


def extract_data(url):
    """
    Creates Soup object and then extracts data from the page.

    Parameters:
    - url (str) : URL of page you want data extracted.

    Returns:
    - Data (dict) : Dictionary of the extracted values.
    """
    try:    
        # Starts at first parid
        html = render_page_with_retry(url)
        # Stainer to limit the data parsed by BeautifulSoup obj
        table_strainer = SoupStrainer('table', class_='quickinfo_subgrp')
        # Create Soup Object
        soup = BeautifulSoup(html, 'html.parser', parse_only=table_strainer)
        # Soup Iterables
        table_headers = soup('th')
        spans = soup('span', class_='ng-binding ng-scope', limit=2)
        # Owner Data
        property_address = get_owner_data('situs 1', table_headers)
        owner_name = get_owner_data('owner 1', table_headers)
        owner_address = get_owner_data('mail address', table_headers)
        # Sales Data
        grantor, grantee, sale_value = get_sales_data(spans)
    
        return {
            'owner_name' : owner_name,
            'property_address' : property_address,
            'owner_address' : owner_address,
            'grantor' : grantor[0],
            'grantee' : grantee[0],
            'price' : sale_value
        }
    
    except Exception as e:
        print(f"Exception from extract data : {e}")
        return None


def find_next_url(curr_url):
    """
    This function uses a Selenium WebDriver to open a headless Chromium browser,
    locates and clicks the next page button, and returns the new current_url.

    Parameters:
    - curr_url (str): The current URL to start the navigation from.

    Returns:
    - str: The new URL after clicking the next page button.
    """
    try: 
        # Creating options object to pass into driver
        options = Options()
        # Headless allows for the browser to work without having a UI
        options.add_argument('--headless')
        # Creates driver and finds page for the curr_url
        driver = webdriver.Chrome(options=options)
        driver.get(f"{curr_url}")
        # Wait Obj
        wait = WebDriverWait(driver, 10)
        # Divs iterable
        divs = driver.find_elements(By.CLASS_NAME, 'w3-bar-item')
        # Finds, Waits, and Clicks on next_button element
        next_button = wait.until(EC.element_to_be_clickable(divs[19].find_elements(By.TAG_NAME, 'i')[1]))
        next_button.click()
        # Waits until url_changes
        wait.until(EC.url_changes(driver.current_url))
        # Saves new url
        new_url = driver.current_url

    except TimeoutException:
         print("TimeOutException: Element not found within the specified time.")
         new_url = None

    except NoSuchElementException:
         print("NoSuchElementException: Element not found.")   
         new_url = None
    
    finally:
        driver.quit()
    
    return new_url


def scraper (curr_url):
    """
    A Web-Scraper for the Whashoe Assessor Site. Uses BeautifulSoup, Selenium, Request-HTML in order to create a dictionary.

    Parameters:
    - curr_url (str) : The current url that needs to have data extracted.

    Return:
    - results (dict) : {'owner_name': str, 'property_address': str, 'owner_address': str, 'grantor': str, 'grantee': str, 'price': str, 'next_url': str}
    """
    try:
        # First: Use BeautifulSoup and Request-HTML helper functions to extract property and owner data, save to result Var.
        result = extract_data(curr_url)
        # add next_url key-val pair to the result dictionary.
        result['next_url'] = find_next_url(curr_url)
        # finally return the dictionary.
        return result
    
    except Exception as e:
        print(f'Exception from scraper : {e}')