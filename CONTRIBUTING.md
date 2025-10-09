# Contributing to QA Automation Scripts

Thank you for your interest in contributing to this project! This document provides guidelines for contributing to the QA Automation Scripts repository.

## 🌟 Ways to Contribute

- **Bug Reports**: Report issues or unexpected behavior
- **Feature Requests**: Suggest new functionality or improvements  
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve README, code comments, or add examples
- **Testing**: Add test cases or improve existing tests

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ for Python scripts
- Node.js 16+ for TypeScript API tests
- Git for version control
- A text editor or IDE

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/qa-automation-scripts.git
   cd qa-automation-scripts
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv qa-env
   source qa-env/bin/activate  # On Windows: qa-env\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   cd qaAutomation/api_automation && npm install
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Contribution Guidelines

### Code Style

#### Python
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes:
  ```python
  def extract_pdf_content(pdf_path: str) -> Dict[int, str]:
      """
      Extract text content from PDF pages.
      
      Args:
          pdf_path: Path to the PDF file
          
      Returns:
          Dictionary mapping page numbers to text content
      """
  ```
- Use type hints where appropriate
- Keep functions focused and single-purpose

#### TypeScript
- Follow consistent naming conventions (camelCase)
- Use TypeScript types and interfaces
- Add JSDoc comments for complex functions:
  ```typescript
  /**
   * Logs into the API and returns authentication token
   * @param baseURL - API base URL
   * @param credentials - Login credentials
   * @returns Promise resolving to API response
   */
  export const login = async (baseURL: string, credentials: any) => {
  ```

#### General
- Use consistent indentation (4 spaces for Python, 2 for TypeScript)
- Remove trailing whitespace
- End files with a newline
- Keep lines under 100 characters when reasonable

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add PDF hyperlink extraction with PyMuPDF support"
git commit -m "Fix image count mismatch in tolerance mode"
git commit -m "Update API tests to handle new authentication flow"

# Avoid
git commit -m "fix bug"
git commit -m "update"
git commit -m "changes"
```

Format: `<type>: <description>`

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation updates
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

### Testing

#### Python Scripts
Before submitting:
1. **Test with sample data** to ensure scripts work as expected
2. **Check error handling** with invalid inputs
3. **Verify output formats** (HTML reports, logs, etc.)
4. **Test with different document formats** when applicable

#### TypeScript Tests
1. **Run existing tests**: `npm test`
2. **Add tests for new features**
3. **Ensure tests pass** before submitting
4. **Update test data** if needed

### Documentation

- Update README.md if adding new features
- Add inline comments for complex logic
- Include usage examples for new functionality
- Update configuration instructions if needed

## 🐛 Reporting Issues

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected vs actual behavior**
4. **Environment details**:
   - Python version
   - Operating system
   - Relevant package versions
   - Sample files (if applicable)
5. **Error messages** or logs
6. **Screenshots** for UI-related issues

### Issue Template
```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version: 
- OS: 
- Package versions: 

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

For new features, please include:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives considered**: Other approaches you've thought of
4. **Implementation details**: Technical considerations (if any)

## 🔄 Pull Request Process

1. **Ensure your branch is up-to-date**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature-name
   git rebase main
   ```

2. **Test your changes thoroughly**
3. **Update documentation** if needed
4. **Submit a pull request** with:
   - Clear title and description
   - Reference any related issues
   - List of changes made
   - Testing performed

### Pull Request Template
```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123

## Changes Made
- Change 1
- Change 2

## Testing
- [ ] Tested with sample documents
- [ ] All existing tests pass
- [ ] Added new tests (if applicable)

## Documentation
- [ ] Updated README (if needed)
- [ ] Added code comments
- [ ] Updated configuration examples
```

## 📝 Development Notes

### Adding New Scripts

When adding new Python scripts:
1. **Follow the existing pattern**: Configuration at top, main logic in functions
2. **Add error handling**: Gracefully handle missing files, invalid formats
3. **Generate reports**: Output should be in HTML or structured format
4. **Use placeholders**: Replace any hardcoded paths or credentials

### Extending API Tests

For new API functionality:
1. **Add to appropriate spec file** or create a new one
2. **Follow existing patterns**: Use shared authentication, consistent assertions
3. **Handle environments**: Support dev/staging/production configurations  
4. **Add proper cleanup**: Restore state after tests

### Supporting New Document Formats

When adding support for new formats:
1. **Research libraries**: Choose well-maintained, reliable packages
2. **Add fallback options**: Handle cases where libraries aren't available
3. **Update requirements.txt**: Include new dependencies
4. **Test thoroughly**: Various document structures and edge cases

## 🎯 Priorities

Current areas where contributions are especially welcome:

### High Priority
- **Enhanced error handling** in Python scripts
- **Additional document format support** (Word, Excel, etc.)
- **Performance optimizations** for large documents
- **Cross-platform testing** and compatibility

### Medium Priority  
- **Additional API test scenarios**
- **Improved reporting formats** (JSON, CSV outputs)
- **Configuration management** improvements
- **Logging standardization**

### Low Priority
- **Code style improvements**
- **Additional utility functions**
- **Documentation enhancements**
- **Example configurations**

## 💬 Community

- **Be respectful** and professional in all interactions
- **Help others** who are contributing or asking questions
- **Share knowledge** and best practices
- **Provide constructive feedback** on code reviews

## ❓ Questions?

If you have questions about contributing:

1. **Check existing issues** and discussions
2. **Review this document** and the README
3. **Open a discussion** or issue for clarification
4. **Tag maintainers** if needed for urgent questions

Thank you for contributing to make this project better! 🎉