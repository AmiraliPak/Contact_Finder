# Contact Finder

A powerful web scraping API that extracts contact information and social media links from websites.

## Overview

Contact Finder is a Flask-based web service that uses Selenium and BeautifulSoup to scrape websites for:

- Social media links (Twitter, LinkedIn, Facebook, Instagram, etc.)
- Email addresses
- Phone numbers

The service provides a secure API endpoint that processes URLs and returns structured JSON data containing all contact information found on the target website.

## Features

- Headless Chrome browser for efficient scraping
- Smart waiting mechanism to ensure JavaScript-loaded content is captured
- Regex pattern matching for emails and phone numbers
- API key authentication for security
- Comprehensive error handling and detailed logging
- Support for a wide range of social media platforms

## Installation

### Prerequisites

- Python 3.6+
- Chrome browser
- ChromeDriver compatible with your Chrome version

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/contact-finder.git
   cd contact-finder
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API key:
   ```
   MY_API_SECRET=your_secure_api_key_here

   # 'True' for debugging - Optional - Default: False
   DEBUG=False

   # Optional - e.g. '/usr/bin/chromedriver'
   # Set the path if "driver not found" error is encountered.
   DRIVER_PATH=path_to_chromedriver
   ```

## Usage

### Running the Server

```
python Contact_Finder.py
```

The server will start on port 5000 by default.

### API Endpoint

**POST /extract-info**

Headers:
- `Content-Type: application/json`
- `api-key: your_secure_api_key_here`

Request Body:
```json
{
  "url": "https://example.com"
}
```

Example Response:
```json
{
  "logo_url": "https://example.com/logo.co",
  "social_links": {
    "LINKEDIN": ["https://www.linkedin.com/company/example"],
    "X": ["https://twitter.com/example"]
  },
  "emails": [
    "contact@example.com",
    "support@example.com"
  ],
  "phone_numbers": [
    "+1-555-123-4567"
  ]
}
```

## Configuration

The application uses Chrome in headless mode with several options to optimize performance and reliability:

```python
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
```

You can modify these options in the `Contact_Finder.py` file.

## Debugging

When running in debug mode, the application saves the HTML source of scraped pages to `debug_page_source.html` for troubleshooting purposes.

## Deployment

For production deployment:

1. Set `debug=False` in the app.run() statement
2. Use a production WSGI server like Gunicorn
3. Consider setting up a reverse proxy with Nginx

Example production startup with Gunicorn:
```
gunicorn -w 4 -b 0.0.0.0:5000 "Contact_Finder:app"
```

Example production startup using Docker:
```
docker compose up -d
docker compose logs -f # Run to see logs
```

## Security Considerations

- Use HTTPS in production
- Regularly rotate your API key
- Consider implementing rate limiting for production use

## License

[MIT](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 