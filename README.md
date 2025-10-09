# QA Automation Scripts

A comprehensive collection of quality assurance automation tools for document verification, format validation, and API testing. This repository contains production-ready QA scripts that have been sanitized and generalized for public use.

## 🚀 Features

### Document Format Verification
- **PDF vs Markdown Image Verification**: Automated comparison of image counts between PDF pages and corresponding Markdown files
- **Cross-format Content Validation**: Compare content across PDF, Markdown, and PowerPoint formats
- **Table Format Validation**: Verify proper Markdown table formatting and structure
- **Link Validation**: Extract and validate hyperlinks from PDF documents and Markdown files

### API Test Automation
- **RESTful API Testing**: Comprehensive TypeScript-based test suites for API endpoints
- **Authentication Workflows**: Automated login and token management
- **Document Management**: API tests for document creation, editing, and publishing workflows
- **AWS S3 Integration**: Automated testing of cloud storage operations

### Content Analysis Tools
- **Language Detection**: Identify and validate content language across documents
- **Similarity Analysis**: Compare document versions and detect changes
- **Code Block Verification**: Validate code snippets and formatting consistency

## 🛠️ What Was Sanitized

For security and privacy, the following sensitive information has been replaced with configurable placeholders:

- **File Paths**: `E:\Verifications\...` → `path/to/your/files`
- **API Endpoints**: Company-specific URLs → `<API_BASE_URL>`
- **Credentials**: Email addresses → `<EMAIL_PLACEHOLDER>`, passwords → `<PASSWORD_PLACEHOLDER>`
- **Document IDs**: UUIDs → `<DOCUMENT_ID_PLACEHOLDER>`
- **AWS Resources**: Bucket names → `<AWS_S3_BUCKET_NAME>`, credentials → `<AWS_CREDENTIALS>`

## 📋 Prerequisites

**For Python Scripts:**
- Python 3.8 or higher
- pip (Python package installer)

**For TypeScript/API Scripts:**
- Node.js 16 or higher
- npm or yarn package manager

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/qa-automation-scripts.git
cd qa-automation-scripts
```

### 2. Set Up Python Environment
```bash
# Create virtual environment (recommended)
python -m venv qa-env
source qa-env/bin/activate  # On Windows: qa-env\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up TypeScript Environment
```bash
# Navigate to API automation folder
cd qaAutomation/api_automation

# Install Node.js dependencies
npm install
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root with your configuration:

```bash
# API Configuration
API_BASE_URL=https://your-api.com/v1
DOCUMENT_ID=your-document-id

# AWS Configuration (for S3 integration tests)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_SESSION_TOKEN=your-aws-session-token
AWS_S3_BUCKET_NAME=your-s3-bucket

# Authentication
DEV_EMAIL=your-dev-email@company.com
DEV_PASSWORD=your-dev-password
STAGING_EMAIL=your-staging-email@company.com
STAGING_PASSWORD=your-staging-password
```

### Script Configuration
Update file paths in the Python scripts to point to your actual documents:

```python
# In Python scripts, update these variables:
PDF_FILE = "path/to/your/document.pdf"
MD_FOLDER = "path/to/your/markdown/folder"
OUTPUT_HTML = "path/to/output/report.html"
```

## 📁 Project Structure

```
qa-automation-scripts/
├── README.md
├── requirements.txt
├── .gitignore
├── guides_format_scripts/
│   ├── comparison_scripts/           # Document comparison tools
│   │   ├── image_verification.py    # PDF vs Markdown image count verification
│   │   ├── markdown_pdf_verification.py
│   │   ├── markdown_to_markdown.py  # Version comparison
│   │   ├── new_old_version.py       # PowerPoint comparison
│   │   ├── pdf_markdown_verification.py
│   │   └── ppt_markdown_verification.py
│   └── format_verification_scripts/ # Format validation tools
│       ├── codeblocks_verification.py
│       ├── landscape_verification.py
│       ├── markdown_format_verification.py
│       ├── markdown_links_formatting.py  # PDF hyperlink extraction
│       └── ppt_format_verification.py
└── qaAutomation/
    └── api_automation/              # TypeScript API testing
        ├── package.json
        ├── tsconfig.json
        ├── mocha.conf.ts
        ├── api/
        │   ├── apiActions.ts        # HTTP request handlers
        │   └── payloads.ts          # Request payload builders
        ├── tests/
        │   ├── .env                 # Environment configuration
        │   ├── englishReview.spec.ts
        │   ├── translationReview.spec.ts
        │   └── s3conFile.ts         # AWS S3 integration tests
        └── jsonFile/
            └── translationReviewPortal.json  # Credential templates
```

## 🎯 Usage Examples

### Document Verification Scripts

#### Image Count Verification
Compare image counts between PDF pages and corresponding Markdown files:

```bash
cd guides_format_scripts/comparison_scripts
python image_verification.py
```

This generates an HTML report showing:
- Image count per PDF page vs Markdown file
- Mismatch details and confidence levels
- Configurable tolerance settings

#### Content Similarity Analysis
Compare text content between different document formats:

```bash
python markdown_pdf_verification.py    # PDF vs Markdown content
python markdown_to_markdown.py         # Version comparison
python ppt_markdown_verification.py    # PowerPoint vs Markdown
```

#### Format Validation
Validate document formatting and structure:

```bash
cd ../format_verification_scripts
python markdown_format_verification.py  # Table format, links, metadata
python codeblocks_verification.py      # Code block consistency
python landscape_verification.py       # PowerPoint slide structure
```

#### Hyperlink Extraction
Extract and analyze hyperlinks from PDF documents:

```bash
python markdown_links_formatting.py
```

Features:
- Comprehensive link detection (external URLs, internal page jumps, annotations)
- Markdown file matching and validation
- HTML reports with link analysis
- Support for multiple PDF libraries (PyMuPDF, pdfplumber, PyPDF2)

### API Test Automation

#### Run All Tests
```bash
cd qaAutomation/api_automation
npm test
```

#### Run Specific Test Suites
```bash
# English review workflow
npx mocha --require ts-node/register tests/englishReview.spec.ts

# Translation review workflow  
npx mocha --require ts-node/register tests/translationReview.spec.ts

# AWS S3 integration tests
npx mocha --require ts-node/register tests/s3conFile.ts
```

#### Generate Test Reports
The tests automatically generate Mochawesome HTML reports in the `mochawesome-report/` directory.

## 🔧 Customization

### Python Scripts Configuration

Most Python scripts include configuration sections at the top:

```python
# image_verification.py example
PDF_FILE = r"path/to/your/document.pdf"
MD_FOLDER = r"path/to/your/markdown/folder" 
OUTPUT_HTML = r"image_verification_report.html"

# Configuration options
PAGE_OFFSET = 0  # Adjust if MD file numbering doesn't match PDF pages
TOLERANCE_MODE = True  # Allow PDF to have >= MD image count
STRICT_PYMUPDF_APPEARANCE_MODE = True  # Enhanced image detection
```

### API Test Configuration

Update the test configuration in each spec file:

```typescript
// Update these variables for your environment
const env = "staging"  // "dev", "staging", "production"
const documentID = "your-document-id";
const baseURL = "https://your-api.com/v1";
const expectedCount = 5;  // Expected number of subdocuments
```

### Environment-Specific Settings

Use environment variables or update the `.env` file for different deployment environments:

```bash
# Development
API_BASE_URL=https://dev-api.company.com/v1

# Staging  
API_BASE_URL=https://staging-api.company.com/v1

# Production
API_BASE_URL=https://api.company.com/v1
```

## 🧪 Testing Features

### Python Script Testing
- **Image Verification**: Supports multiple PDF processing libraries with fallback options
- **Content Analysis**: TF-IDF vectorization for similarity scoring
- **Format Validation**: XML metadata verification, table structure validation
- **Link Analysis**: Comprehensive hyperlink extraction and validation

### API Test Features
- **Authentication**: Automated login and token management
- **Document Workflows**: Complete document lifecycle testing
- **AWS Integration**: S3 bucket operations and file validation
- **Reporting**: Detailed HTML test reports with screenshots and metrics

## 🔒 Security Best Practices

1. **Never commit credentials** - Use environment variables or secure vaults
2. **Keep `.env` files** out of version control (already in .gitignore)
3. **Use least-privilege** AWS IAM policies for S3 access
4. **Rotate API keys** regularly
5. **Validate inputs** in custom configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines
- Follow existing code style and patterns
- Add docstrings to Python functions
- Include TypeScript type annotations
- Update README for new features
- Test with multiple document formats

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for production QA workflows in enterprise documentation systems
- Designed for scalability and maintainability
- Supports multiple document formats and processing libraries

## ⚠️ Disclaimer

This repository contains generalized versions of production QA tools. Some functionality may require additional setup or customization for your specific use case. Always test thoroughly in a development environment before production use.
