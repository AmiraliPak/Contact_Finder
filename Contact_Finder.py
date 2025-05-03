# grand_spider.py (Updated to wait for specific social link)

from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # For explicit waits
from selenium.webdriver.support import expected_conditions as EC # For explicit waits
from selenium.webdriver.common.by import By # For explicit waits selectors
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote, urljoin
import time # Keep time for potential future use, though not for main wait now
import os
import re
from dotenv import load_dotenv
import traceback # For detailed error logging
import requests

# --- Load environment variables from .env file ---
load_dotenv()

# --- Configuration ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--window-size=1920,1080") # Consider uncommenting if issues persist
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Define social media domains
SOCIAL_MEDIA_DOMAINS = {
  'twitter.com', 'x.com', 'facebook.com', 'fb.com', 'instagram.com', 'linkedin.com',
  'youtube.com', 'youtu.be', 'pinterest.com', 'tiktok.com', 'snapchat.com', 'reddit.com',
  'tumblr.com', 'whatsapp.com', 'wa.me', 't.me', 'telegram.me', 'discord.gg',
  'discord.com', 'medium.com', 'github.com', 'threads.net', 'mastodon.social',
}

# --- Regex Patterns ---
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,}"

# --- Flask App Setup ---
app = Flask(__name__)

def normalize_url(url):
    """Normalize URL to get the landing page URL."""
    if not url:
        return None
        
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    try:
        # Make a HEAD request to check for redirects
        response = requests.head(url, allow_redirects=True, timeout=10)
        final_url = response.url
        
        # Parse the URL to get the base domain
        parsed = urlparse(final_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        return base_url
    except Exception as e:
        print(f"Error normalizing URL {url}: {e}")
        return None

# --- API Endpoint ---
@app.route('/extract-info', methods=['POST'])
def extract_info():
    # --- Authentication ---
    api_key = request.headers.get('api-key')
    expected_key = os.environ.get("MY_API_SECRET")
    if not expected_key:
        print("ERROR: MY_API_SECRET environment variable not found.")
        return jsonify({"error": "Server configuration error"}), 500
    if not api_key or api_key != expected_key:
        print(f"Unauthorized attempt.")
        return jsonify({"error": "Unauthorized"}), 401

    # --- Get URL from Request Body ---
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400
    print(f"\n--- New Request ---")
    target_url = normalize_url(data['url'])
    if not target_url:
        return jsonify({"error": "Invalid or unreachable URL"}), 400
    print(f"Target URL: {target_url}")

    # --- Scrape using Selenium ---
    driver = None
    social_links_found = set()
    emails_found = set()
    phones_found = set()

    try:
        driver_path = os.environ.get("DRIVER_PATH")
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(45) # Timeout for initial page load request

        print(f"Attempting to load URL: {target_url}")
        driver.get(target_url)
        print(f"Initial page load initiated. Waiting for specific content (max 20s)...")

        # --- Explicit Wait ---
        # Wait for a specific element that likely appears after JS loading,
        # such as one of the social media links.
        wait_timeout = 20 # seconds
        # *** UPDATED SELECTOR: Waiting for an anchor tag with href containing 'twitter.com' ***
        # You could change 'twitter.com' to 'linkedin.com' or another expected social domain
        # if that proves more reliable for the sites you target.
        wait_selector = (By.CSS_SELECTOR, "a[href*='twitter.com']")
        try:
            wait = WebDriverWait(driver, wait_timeout)
            print(f"Waiting up to {wait_timeout}s for element matching CSS selector: \"{wait_selector[1]}\"")
            wait.until(EC.presence_of_element_located(wait_selector))
            print(f"Element matching selector found. Proceeding to get source.")
        except TimeoutException:
            # This means the specific social link wasn't found within the wait_timeout
            print(f"WARNING: Timed out after {wait_timeout}s waiting for element matching \"{wait_selector[1]}\".")
            print("         Page might be incomplete, blocked, or the element selector needs adjustment.")
            # Continue anyway, maybe other data (email/phone) is present or loaded earlier.

        # --- Get Page Source ---
        page_source = driver.page_source
        source_length = len(page_source) if page_source else 0
        print(f"Got page source, length: {source_length}")

        # --- DEBUG: Save HTML Source ---
        if app.debug:
            try:
                debug_filename = "debug_page_source.html"
                with open(debug_filename, "w", encoding="utf-8") as f:
                    f.write(page_source if page_source else "<html><body>Error: Page source was empty or None</body></html>")
                print(f"Saved page source for debugging to: {debug_filename}")
            except Exception as e:
                print(f"Error saving debug HTML file: {e}")
        # --- End Debug ---

        if not page_source:
             print("WARNING: Page source is empty after wait. Skipping parsing.")
             # Optionally return a specific status or warning in JSON
             return jsonify({
                 "social_links": [],
                 "emails": [],
                 "phone_numbers": [],
                 "logo_url": None,
                 "status": "Warning: Could not retrieve page source or source was empty."
             }), 200 # Return 200 OK but indicate potential issue

        # --- Parse with Beautiful Soup ---
        soup = BeautifulSoup(page_source, 'html.parser')

        # 1. Extract from Links (Social, Mailto, Tel)
        links = soup.find_all('a', href=True)
        print(f"Found {len(links)} total anchor tags for parsing.")
        for link in links:
            href = link.get('href')
            if not href or not isinstance(href, str):
                continue
            href = href.strip()
            if not href:
                continue

            # Check for mailto links
            if href.startswith('mailto:'):
                try:
                    email_part = href.split('mailto:', 1)[1].split('?')[0]
                    if email_part:
                        potential_email = unquote(email_part)
                        if re.fullmatch(EMAIL_REGEX, potential_email):
                           emails_found.add(potential_email)
                except Exception as e:
                    print(f"Error processing mailto link '{href}': {e}")
                continue # Move to next link

            # Check for tel links
            if href.startswith('tel:'):
                try:
                    phone_part = href.split('tel:', 1)[1]
                    cleaned_phone = phone_part.strip()
                    if cleaned_phone:
                       phones_found.add(cleaned_phone)
                except Exception as e:
                    print(f"Error processing tel link '{href}': {e}")
                continue # Move to next link

            # Check for social media links (if not mailto/tel)
            try:
                # Skip non-http links for social media domain check
                if not href.startswith(('http://', 'https://')):
                    continue

                url_obj = urlparse(href)
                # Normalize hostname: remove 'www.' and convert to lowercase
                hostname = url_obj.netloc.lower().replace('www.', '')
                if not hostname:
                    continue

                for social_domain in SOCIAL_MEDIA_DOMAINS:
                    # Check if the hostname exactly matches or ends with .social_domain (for subdomains like blog.twitter.com)
                    if hostname == social_domain or hostname.endswith('.' + social_domain):
                        social_links_found.add(href)
                        # print(f"Found social link: {href}")
                        break # Found a match for this link's domain, check next link tag
            except Exception as parse_err:
                # print(f"Error parsing potential social link '{href}': {parse_err}")
                pass # Ignore errors for individual link parsing

        # 2. Extract from Page Text using Regex (Emails and Phones)
        page_text = ""
        if soup.body:
            page_text = soup.body.get_text(separator=' ', strip=True)
            # print(f"\nPage Text for Regex (first 500 chars):\n{page_text[:500]}\n---")

            # Find emails in text
            try:
                found_emails_in_text = re.findall(EMAIL_REGEX, page_text)
                if found_emails_in_text:
                    emails_found.update(found_emails_in_text)
            except Exception as regex_email_err:
                 print(f"Error running EMAIL_REGEX: {regex_email_err}")

            # Find phone numbers in text
            try:
                found_phones_in_text = re.findall(PHONE_REGEX, page_text)
                if found_phones_in_text:
                    processed_phones = []
                    for p in found_phones_in_text:
                        phone_str = "".join(filter(None, p)) if isinstance(p, tuple) else p
                        if phone_str:
                             processed_phones.append(phone_str.strip())
                    phones_found.update(processed_phones)
            except Exception as regex_phone_err:
                print(f"Error running PHONE_REGEX: {regex_phone_err}")
        else:
            print("WARNING: Could not find body tag in HTML source for text extraction.")


        print(f"Extraction complete. Found: {len(social_links_found)} social, {len(emails_found)} emails, {len(phones_found)} phones.")
        
        # Extract logo URL
        logo_url = extract_logo_url(soup, target_url)
        
        return jsonify({
            "social_links": sorted(list(social_links_found)),
            "emails": sorted(list(emails_found)),
            "phone_numbers": sorted(list(phones_found)),
            "logo_url": logo_url
        }), 200

    except TimeoutException as e: # Catches the driver.get() timeout OR the explicit wait timeout if not caught inside
        print(f"Timeout error encountered for URL: {target_url}")
        # Differentiate between initial load and element wait timeouts if needed based on context or specific exception args
        print(f"Error details: {e}")
        # If it was the initial load timeout: 504 Gateway Timeout
        # If it was the explicit wait timeout (and not handled inside): Maybe 500 or a custom error
        return jsonify({"error": f"Timeout processing URL: {target_url}. Check logs for details."}), 504 # Or 500
    except WebDriverException as e:
        print(f"WebDriver error processing {target_url}: {e}")
        return jsonify({"error": f"Browser automation error. Check server logs."}), 500
    except Exception as e:
        print(f"Unexpected error in /extract-info for URL {target_url}:")
        traceback.print_exc() # Print full traceback to console/log
        return jsonify({"error": "An internal server error occurred."}), 500
    finally:
        if driver:
            print("Closing WebDriver.")
            driver.quit()

def extract_logo_url(soup, base_url):
    """Extract the logo URL from the webpage with improved validation."""
    logo_url = None
    
    # Try to get the base domain for relative URLs
    try:
        parsed_url = urlparse(base_url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    except:
        base_domain = base_url

    def normalize_url(url):
        """Convert relative URLs to absolute URLs."""
        if not url:
            return None
        if not url.startswith(('http://', 'https://')):
            return base_domain + ('/' if not url.startswith('/') else '') + url
        return url

    def is_likely_logo(img_element):
        """Validate if an image element is likely to be a logo."""
        if not img_element:
            return False
            
        # Check image dimensions (logos are typically square-ish and not too large)
        width = img_element.get('width')
        height = img_element.get('height')
        if width and height:
            try:
                w = int(width)
                h = int(height)
                # Logos are typically not too large and maintain reasonable aspect ratio
                if w > 500 or h > 500 or (w > 0 and h > 0 and (w/h > 3 or h/w > 3)):
                    return False
            except ValueError:
                pass

        # Check if image is in header/navbar
        parent = img_element.parent
        while parent:
            parent_class = parent.get('class', [])
            parent_id = parent.get('id', '')
            if any(x in str(parent_class).lower() or x in str(parent_id).lower() 
                  for x in ['header', 'navbar', 'nav', 'brand', 'logo']):
                return True
            parent = parent.parent

        return False

    # 1. Check for favicon/shortcut icon (most reliable for brand identity)
    favicon = soup.find('link', rel=lambda x: x and ('icon' in x.lower() or 'shortcut' in x.lower()))
    if favicon and favicon.get('href'):
        return normalize_url(favicon['href'])

    # 2. Check for og:image meta tag (usually the main brand image)
    og_image = soup.find('meta', property='og:image')
    if og_image and og_image.get('content'):
        return normalize_url(og_image['content'])

    # 3. Look for logo in header/navbar first
    header = soup.find(['header', 'nav'], class_=lambda x: x and any(term in str(x).lower() 
                                                                     for term in ['header', 'navbar', 'nav']))
    if header:
        # Look for images with logo-related attributes
        logo_img = header.find('img', 
                             attrs={'alt': lambda x: x and any(term in str(x).lower() 
                                                             for term in ['logo', 'brand'])})
        if logo_img and logo_img.get('src'):
            return normalize_url(logo_img['src'])

    # 4. Look for images with specific logo-related attributes
    logo_patterns = [
        'logo', 'brand', 'header-logo', 'site-logo', 'company-logo',
        'navbar-logo', 'nav-logo', 'header-brand', 'site-brand'
    ]
    
    for pattern in logo_patterns:
        # Check by ID
        logo_img = soup.find('img', id=lambda x: x and pattern in str(x).lower())
        if logo_img and is_likely_logo(logo_img) and logo_img.get('src'):
            return normalize_url(logo_img['src'])
            
        # Check by class
        logo_img = soup.find('img', class_=lambda x: x and pattern in str(x).lower())
        if logo_img and is_likely_logo(logo_img) and logo_img.get('src'):
            return normalize_url(logo_img['src'])

    # 5. As a last resort, look for the first image in the header that might be a logo
    if header:
        for img in header.find_all('img'):
            if is_likely_logo(img) and img.get('src'):
                return normalize_url(img['src'])

    return None

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "active"}), 200

# --- Run the Flask App ---
if __name__ == '__main__':
    # Set debug=False when deploying to production
    debug = (os.environ.get("DEBUG") == "True")
    app.run(host='0.0.0.0', port=5000, debug=debug)
