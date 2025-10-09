# QA Automation Framework

Comprehensive testing toolkit for document verification, API validation, UI automation, and performance testing.

## 🚀 Quick Start

```bash
# Python setup for document testing
pip install -r requirements.txt
python file_formatting_scripts/comparison_scripts/image_verification.py

# API testing setup
cd automation/api_automation
npm install
npm test

# Performance testing
cd performanceTesting/k6_productCreationScript
k6 run mainSuite/main.js
```

## 📁 Project Structure

```
├── file_formatting_scripts/     # Document verification tools
│   ├── comparison_scripts/      # Cross-format comparison (PDF ↔ Markdown)
│   └── format_verification_scripts/ # Format validation & link extraction
├── automation/
│   ├── api_automation/          # REST API testing (TypeScript/Mocha)
│   └── uiAutomation/           # Browser testing (WebdriverIO/Cucumber)
└── performanceTesting/
    ├── k6_productCreationScript/ # K6 load testing
    └── chatWithDocumentScript/   # Chat API performance testing
```

## 🛠 Technology Stack

| Component | Technologies |
|-----------|-------------|
| **Document Testing** | Python, PyMuPDF, pdfplumber, BeautifulSoup |
| **API Testing** | TypeScript, Mocha, Chai, Axios |
| **UI Testing** | WebdriverIO, Cucumber, TypeScript |
| **Performance Testing** | K6, JavaScript |

## 📋 Testing Capabilities

### Document Verification
- **Image count comparison** between PDF and Markdown
- **Content similarity analysis** across formats
- **Hyperlink extraction** and validation
- **Table structure verification**
- **Code block consistency** checks

### API Testing
- **Authentication workflows** with multi-environment support
- **CRUD operations** validation
- **AWS S3 integration** testing
- **Knowledge base document** management

### UI Automation
- **Machine learning model training** workflows
- **Data pipeline configuration** testing
- **BDD scenarios** with Cucumber
- **Page Object Model** architecture

### Performance Testing
- **Load testing** with configurable virtual users
- **API response time** measurement
- **Concurrent request** handling
- **Chat API performance** evaluation

## ⚙️ Configuration

All frameworks use environment variables for configuration:

```bash
# Copy example configs
cp performanceTesting/k6_productCreationScript/.env.example .env

# Update with your values
API_BASE_URL=https://your-api.com
TEST_USERNAME=your_username
TEST_PASSWORD=your_password
```

## 🚀 Usage Examples

### Document Verification
```bash
# Verify image counts between PDF and Markdown
python file_formatting_scripts/comparison_scripts/image_verification.py

# Extract and validate hyperlinks
python file_formatting_scripts/format_verification_scripts/markdown_links_formatting.py
```

### API Testing
```bash
cd automation/api_automation
npm test                    # Run all tests
npm run test:specific      # Run specific test suite
```

### Performance Testing
```bash
cd performanceTesting/k6_productCreationScript

# Basic load test
k6 run mainSuite/main.js

# Custom load test
k6 run --vus 50 --duration 5m mainSuite/main.js
```

## 📊 Features

✅ **Multi-format document validation**  
✅ **Cross-browser UI testing**  
✅ **RESTful API comprehensive testing**  
✅ **Load and performance testing**  
✅ **Environment-driven configuration**  
✅ **Detailed HTML reporting**  
✅ **CI/CD pipeline ready**

## � Security

- No hardcoded credentials
- Environment variable configuration
- Sanitized for public repositories
- Configurable authentication methods

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Ready to use**: All scripts are sanitized and production-ready. Configure environment variables and start testing!