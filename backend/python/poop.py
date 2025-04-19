import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Union, Any
from requests.exceptions import RequestException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEFAULT_DOMAIN = 'poop.run'
HEADERS: Dict[str, str] = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}

class PoopFile:
    """Class for retrieving file information from PoopHD URLs.
    
    This class handles the extraction of file metadata from various PoopHD URLs,
    including single files and folders containing multiple files.
    """
    
    def __init__(self) -> None:
        """Initialize the PoopFile class with empty file list and session."""
        self.file: List[Dict[str, str]] = []
        self.domain: str = ''
        self.r = requests.Session()
        self.headers: Dict[str, str] = HEADERS.copy()

    #--> Redirect ke URL asli (yg msh aktif)
    def redirect(self, url:str) -> None:
        return(self.r.head(url, headers=self.headers, allow_redirects=True).url)

    def getAllFile(self, url: str) -> None:
        """Get all files from a URL.
        
        This method handles different types of URLs (single file, folder, trending)
        and extracts file information accordingly.
        
        Args:
            url: The URL to extract files from
        """
        try:
            # Handle blocked URLs (Internet positif)
            if '/e/' in str(url):
                id_value: str = url.replace('//','/').split('/')[-1].split('?')[0].lower()
                new_url = f'https://{DEFAULT_DOMAIN}/d/{id_value}'
                self.getAllFile(new_url)
                return

            # Get redirect URL
            base_url: str = self.redirect(url).split('?')[0]

            # Get HTML response
            response = self.r.get(base_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Non-200 status code: {response.status_code} for URL {base_url}")
                return
                
            self.domain: str = response.url.replace('//','/').split('/')[1]

            # Clean and parse HTML
            cleaned_html = response.text.replace('\\','').replace('\n','')
            soup_str: str = self._clean_soup(BeautifulSoup(cleaned_html, 'html.parser'))

            # Determine URL type and process accordingly
            type_url: str = response.url.replace('//','/').split('/')[2].lower()

            if type_url == 'f':  # Folder content
                self._process_folder(soup_str)
            elif type_url == 'd':  # Single file
                self.singleFile(response.url)
            elif type_url == 'top':  # Trending content
                self._process_trending()
                
        except RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error processing URL {url}: {str(e)}")
            
    def _clean_soup(self, soup: BeautifulSoup) -> str:
        """Clean and format BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup object to clean
            
        Returns:
            Cleaned HTML string
        """
        return soup.prettify().replace('\n', '').replace('  ', '').replace('> <','><')
        
    def _process_folder(self, soup_str: str) -> None:
        """Process folder content.
        
        Args:
            soup_str: HTML string of folder page
        """
        list_page = list(dict.fromkeys(self.getAllPage(soup_str)))
        for page_url in list_page:
            try:
                response = self.r.get(page_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup_str = self._clean_soup(BeautifulSoup(response.text.replace('\\','').replace('\n',''), 'html.parser'))
                    self.multiFile(soup_str)
            except Exception as e:
                logger.warning(f"Error processing page {page_url}: {str(e)}")
                continue
                
    def _process_trending(self) -> None:
        """Process trending content pages."""
        for i in range(1, 11):
            try:
                response = self.r.get(f'https://{self.domain}/top?p={i}', headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup_str = self._clean_soup(BeautifulSoup(response.text.replace('\\','').replace('\n',''), 'html.parser'))
                    self.multiFile(soup_str)
            except Exception as e:
                logger.warning(f"Error processing trending page {i}: {str(e)}")
                continue

    def getAllPage(self, soup: str) -> List[str]:
        """Extract all page URLs from a folder page.
        
        Args:
            soup: HTML string to extract page links from
            
        Returns:
            List of page URLs
        """
        try:
            return [f'https://{self.domain}{i}' for i in re.findall(r'<a class="page-link" href="(.*?)">.*?</a>', str(soup))]
        except Exception as e:
            logger.error(f"Error extracting page links: {str(e)}")
            return []

    def multiFile(self, soup: str) -> None:
        """Extract multiple files from a page.
        
        Args:
            soup: HTML string to extract file information from
        """
        try:
            # Find all div elements
            divs = re.findall(r'<div class=\".*?\">(.*?)</div>', str(soup))
            
            # Filter divs containing video information
            video_divs = [div for div in divs if 'strong' in div]
            
            for div in video_divs:
                try:
                    # Extract video information
                    href_match = re.search(r'href="(.*?)"', str(div))
                    name_match = re.search(r'<strong>(.*?)</strong>', str(div))
                    image_match = re.search(r'src="(.*?)"', str(div))
                    
                    if href_match and name_match and image_match:
                        id_value = href_match.group(1).split('/')[-1].split('?')[0]
                        name = name_match.group(1).strip()
                        image = image_match.group(1)
                        
                        # Create file item and add to list
                        item: Dict[str, str] = {
                            'domain': self.domain,
                            'id': id_value,
                            'name': name,
                            'image': image
                        }
                        
                        # Check for duplicates before adding
                        if not any(existing['id'] == id_value for existing in self.file):
                            self.file.append(item)
                except Exception as e:
                    logger.debug(f"Error extracting video info: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Error processing multiple files: {str(e)}")
            return

    def singleFile(self, url: str) -> None:
        """Extract information from a single file URL.
        
        Args:
            url: URL of the single file
        """
        try:
            response = self.r.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Non-200 status code: {response.status_code} for URL {url}")
                return
                
            soup_str = self._clean_soup(BeautifulSoup(response.text.replace('\\','').replace('\n',''), 'html.parser'))
            
            # Extract file information
            id_value = url.replace('//','/').split('/')[-1].split('?')[0]
            
            name_match = re.search(r'<h4>(.*?)</h4>', str(soup_str))
            image_match = re.search(r'<img alt=\".*?\" class=\".*?\" src="(.*?)"', str(soup_str))
            
            if name_match and image_match:
                name = name_match.group(1).strip()
                image = image_match.group(1)
                
                # Create file item and add to list
                item: Dict[str, str] = {
                    'domain': self.domain,
                    'id': id_value,
                    'name': name,
                    'image': image
                }
                
                # Check for duplicates before adding
                if not any(existing['id'] == id_value for existing in self.file):
                    self.file.append(item)
            else:
                logger.warning(f"Could not extract name or image for URL {url}")
                
        except Exception as e:
            logger.error(f"Error processing single file {url}: {str(e)}")
            return

class PoopLink:
    """Class for retrieving download and streaming links from PoopHD files.
    
    This class handles the extraction of direct download and streaming links
    from PoopHD file IDs.
    """
    
    def __init__(self) -> None:
        """Initialize the PoopLink class with empty link and session."""
        self.link: str = ''
        self.r = requests.Session()
        self.headers: Dict[str, str] = HEADERS.copy()

    #--> Redirect ke URL asli (yg msh aktif)
    def redirect(self, url:str) -> None:
        return(self.r.head(url, headers=self.headers, allow_redirects=True).url)

    def getLink(self, domain: str, id_value: str) -> None:
        """Get download and streaming link for a file.
        
        Args:
            domain: Domain of the PoopHD site
            id_value: ID of the file
        """
        try:
            # Step 1: Get redirect URL
            url1 = self.redirect(f'https://{domain}/p0?id={id_value}')
            
            # Step 2: Get headers and second redirect URL
            response = self.r.get(url1, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Non-200 status code: {response.status_code} for URL {url1}")
                return
                
            # Clean and parse HTML
            soup_str = BeautifulSoup(
                response.text.replace('\\','').replace('\n',''), 
                'html.parser'
            ).prettify().replace('\n', '').replace(' ', '').replace('> <','><').replace("'", '"')
            
            # Extract URL and authorization
            url_match = re.search(r'returnfetch\("(.*?)"', str(soup_str))
            auth_match = re.search(r'"Authorization":"(.*?)"', str(soup_str))
            
            if url_match and auth_match:
                url2 = url_match.group(1).strip()
                auth = auth_match.group(1).strip()
                
                # Step 3: Get direct download & streaming URL
                headers = {**self.headers, 'Authorization': auth, 'origin': f'https://{domain}'}
                
                response = self.r.get(url2, headers=headers, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Non-200 status code: {response.status_code} for URL {url2}")
                    return
                    
                try:
                    json_response = response.json()
                    self.link = json_response.get('direct_link', '')
                    if not self.link:
                        logger.warning(f"No direct_link found in response for ID {id_value}")
                except ValueError:
                    logger.error(f"Invalid JSON response for URL {url2}")
            else:
                logger.warning(f"Could not extract URL or authorization for ID {id_value}")
                
        except RequestException as e:
            logger.error(f"Request error for ID {id_value}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error for ID {id_value}: {str(e)}")

def test() -> None:
    """Test function to demonstrate usage of PoopFile and PoopLink classes."""
    # Example PoopHD URLs
    test_urls = [
        'https://poop.vin/d/LPxbX8Mn4KZ',
        'https://poop.pm/f/t8e12zcx7ra',
        'https://poop.pm/f/p6mqkgysdr0',
        'https://poop.pm/f/be20crhis8g',
        'https://poop.pm/f/WTdgWsSnlnv'
    ]
    
    # Example PoopHD IDs
    test_ids = [
        'LPxbX8Mn4KZ',
        'ggvl28sr6tuu',
        'sjg5d1abyi5e',
        '6yz2q62slsir',
        'JJOXFuOZoJL'
    ]
    
    # Test PoopFile
    print("Testing PoopFile...")
    pf = PoopFile()
    pf.getAllFile(test_urls[0])
    print(f"Found {len(pf.file)} files:")
    for item in pf.file:
        print(f"- {item['name']} (ID: {item['id']})")
    
    # Test PoopLink
    print("\nTesting PoopLink...")
    domain = 'poop.run'
    pl = PoopLink()
    pl.getLink(domain, test_ids[0])
    if pl.link:
        print(f"Link found: {pl.link[:60]}...")
    else:
        print("No link found.")

if __name__ == '__main__':
    test()