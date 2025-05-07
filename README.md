# Contact Extractor API

<div align="center">
  <img src="screenshots/Contact_extractor_single_Request.png" alt="Contact Extractor Logo" width="600"/>
  
  [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
  [![Flask](https://img.shields.io/badge/flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
</div>

## 📝 Overview

Contact Extractor is a powerful API service that automatically extracts contact information from websites, including:
- Email addresses
- Phone numbers
- Social media links (Instagram, LinkedIn, X/Twitter, Facebook, and more)
- Other contact-related data

The service provides multiple endpoints for different use cases, from single domain processing to batch processing via CSV or Google Sheets integration.

## ✨ Features

- 🔍 **Intelligent Contact Detection**
  - Advanced email pattern recognition
  - Smart phone number validation
  - Social media link categorization
  - Footer-specific content analysis

- 🚀 **Multiple Processing Methods**
  - Single domain processing
  - Array of domains processing
  - CSV file processing
  - Google Sheets integration

- 🔒 **Security**
  - API key authentication
  - Secure request handling
  - Input validation

- 📊 **Output Options**
  - JSON response with extracted data
  - CSV file generation
  - Structured data format

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/contact-extractor.git
cd contact-extractor
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```env
MY_API_SECRET=your_api_key_here
GOOGLE_SHEET_WORKER_URL=your_google_sheet_worker_url
```

## 🚀 Usage

### Starting the Server

```bash
python Contact_extractor.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### 1. Single Domain Request
Process a single domain for contact information.

**Request:**
```http
POST /single-request
Content-Type: application/json
api-key: your_api_key

{
    "url": "example.com"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Processed 1 domain. CSV generated.",
    "csv_filename": "single_domain_1234567890.csv",
    "results": [...]
}
```

![Single Request Example](screenshots/Contact_extractor_single_Request.png)

#### 2. Array Request
Process multiple domains in parallel.

**Request:**
```http
POST /array-request
Content-Type: application/json
api-key: your_api_key

{
    "domains": ["example1.com", "example2.com"],
    "max_workers": 5
}
```

![Array Request Example](screenshots/Contact_extractor_Array.png)

#### 3. CSV Request
Process domains from a CSV file.

**Request:**
```http
POST /csv-request
Content-Type: application/json
api-key: your_api_key

{
    "csv_url": "https://example.com/domains.csv",
    "domain_column_header": "Domain",
    "max_workers": 5
}
```

![CSV Request Example](screenshots/Contact_extractor_CSV_request.png)

#### 4. Sheet Request
Process domains from a Google Sheet.

**Request:**
```http
POST /sheet-request
Content-Type: application/json
api-key: your_api_key

{
    "target_url": "your_google_sheet_url",
    "max_workers": 5
}
```

![Sheet Request Example](screenshots/Contact_extractor_Sheet.png)

#### 5. Download CSV
Download generated CSV files.

```http
GET /download-csv/{filename}
api-key: your_api_key
```

## 🔧 Configuration

### Environment Variables

- `MY_API_SECRET`: Your API key for authentication
- `GOOGLE_SHEET_WORKER_URL`: URL for Google Sheets integration

### Chrome Options

The service uses headless Chrome for web scraping with the following configurations:
- Headless mode
- No sandbox
- Disabled GPU
- Custom user agent

## 📊 Output Format

The CSV output includes the following columns:
- Domain
- Emails
- Phone Numbers
- Instagram
- LinkedIn
- X (Twitter)
- Facebook
- Other Socials

## 🔒 Security Considerations

1. Always use HTTPS in production
2. Keep your API key secure
3. Validate all input data
4. Monitor request rates
5. Implement rate limiting if needed

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask framework
- Selenium WebDriver
- BeautifulSoup4
- Python-dotenv

---

<div align="center">
  Made with ❤️ by [Your Name]
</div> 