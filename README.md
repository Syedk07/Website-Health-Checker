# SitePulse 🌐

> A lightweight, professional website health monitoring and checking tool built with Python

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-70%20passing-brightgreen.svg)](tests/)

SitePulse is a beginner-friendly desktop application that allows you to monitor the availability and basic technical health of websites. Track HTTP status codes, response times, SSL certificate expiration, and maintain a complete monitoring history - all from a clean, professional desktop interface.

![SitePulse Dashboard](docs/screenshots/dashboard.png)

## ✨ Features

- ✅ **Website Availability Checks** - Monitor if websites are reachable via HTTP/HTTPS
- 📊 **HTTP Status Detection** - Identify response codes (200, 404, 500, etc.)
- ⚡ **Response Time Measurement** - Track how quickly websites respond (milliseconds)
- 🔒 **SSL Certificate Inspection** - Check certificate validity and expiration dates
- 📝 **Monitoring History** - Store and review all check results with SQLite
- 📈 **Health Reports** - Generate availability statistics and response time summaries
- 💾 **CSV Export** - Export monitoring data for external analysis
- 🎨 **Clean Desktop Interface** - Professional dashboard built with Tkinter
- 🔄 **Background Checking** - Non-blocking health checks using threading
- 🌍 **Cross-Platform** - Works on Windows, Linux, and macOS

## 🎯 Screenshots

<table>
  <tr>
    <td><b>Dashboard</b><br/>Monitor all websites at a glance</td>
    <td><b>Website Management</b><br/>Add, edit, and check websites</td>
  </tr>
  <tr>
    <td><b>History</b><br/>Browse complete check history</td>
    <td><b>Reports</b><br/>View statistics and export data</td>
  </tr>
</table>

## 📋 Requirements

- **Python 3.11 or newer** (tested with Python 3.14)
- **Operating System:** Windows, Linux, or macOS
- **Internet Connection:** Required for health checks (not for viewing history)

## 🚀 Installation

### Step 1: Check Python Version

First, verify you have Python 3.11 or newer installed:

```bash
python --version
```

If you need to install Python, download it from [python.org](https://www.python.org/downloads/)

### Step 2: Clone the Repository

```bash
git clone https://github.com/Syedk07/Website-Health-Checker.git
cd Website-Health-Checker
```

**Alternative:** Download the ZIP file from GitHub and extract it.

### Step 3: Create a Virtual Environment

**Windows (PowerShell/Command Prompt):**
```bash
python -m venv venv
```

**Linux/macOS:**
```bash
python3 -m venv venv
```

### Step 4: Activate the Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `requests>=2.31.0` - For HTTP requests
- `pytest>=7.4.0` - For testing (optional)
- `pytest-mock>=3.11.1` - For mocking in tests (optional)

### Step 6: Install SitePulse

Install the application in development mode:

```bash
pip install -e .
```

This makes the `sitepulse` command available system-wide (within your virtual environment).

### ✅ Verify Installation

Check that installation was successful:

```bash
python -c "from sitepulse import __version__; print(f'SitePulse v{__version__} installed successfully!')"
```

You should see: `SitePulse v1.0.0 installed successfully!`

## 🎮 Usage

### Launching the Application

After installation, you can launch SitePulse using either method:

**Method 1: Using the installed command (recommended)**
```bash
sitepulse
```

**Method 2: Running as a Python module**
```bash
python -m sitepulse
```

**Note:** Make sure your virtual environment is activated before running!

### Quick Start Guide

1. **Launch SitePulse**
   ```bash
   sitepulse
   ```

2. **Add Your First Website**
   - Click **"Websites"** in the sidebar
   - Click **"Add Website"** button
   - Enter website details:
     - **Name:** My Website
     - **URL:** https://www.example.com
   - Click **"Save"**

3. **Check Website Health**
   - Select the website from the list
   - Click **"Check Selected"** button
   - Wait for the health check to complete
   - View results: Status, Response Time, SSL Info

4. **View Dashboard**
   - Click **"Dashboard"** in the sidebar
   - See summary: Total websites, Online, Offline, Errors
   - Click **"Check All Websites"** to check all at once

5. **Browse History**
   - Click **"History"** in the sidebar
   - Filter by website or date range
   - View detailed check results

6. **Generate Reports**
   - Click **"Reports"** in the sidebar
   - Select website and time period
   - Click **"Generate Report"**
   - View statistics and export to CSV

### Example Workflow

```bash
# 1. Navigate to project directory
cd Website-Health-Checker

# 2. Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 3. Launch application
sitepulse

# 4. Add websites and monitor!
```

## 🗂️ Project Structure

```
Website-Health-Checker/
├── src/
│   └── sitepulse/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Entry point for module execution
│       ├── app.py               # Main application class
│       ├── database/            # Database management
│       │   ├── __init__.py
│       │   └── db.py           # SQLite operations
│       ├── models/              # Data models
│       │   ├── __init__.py
│       │   ├── website.py      # Website model
│       │   └── check_result.py # Check result model
│       ├── services/            # Business logic
│       │   ├── __init__.py
│       │   ├── health_checker.py   # HTTP health checking
│       │   ├── ssl_checker.py      # SSL certificate inspection
│       │   ├── website_service.py  # Website CRUD operations
│       │   ├── report_service.py   # Report generation
│       │   └── export_service.py   # CSV export
│       ├── ui/                  # User interface
│       │   ├── __init__.py
│       │   ├── main_window.py  # Main application window
│       │   ├── dashboard.py    # Dashboard view
│       │   ├── websites.py     # Website management view
│       │   ├── history.py      # History view
│       │   └── reports.py      # Reports view
│       └── utils/               # Utility functions
│           ├── __init__.py
│           ├── paths.py        # Platform-specific paths
│           └── url_utils.py    # URL validation
├── tests/                       # Test suite (70 tests)
│   ├── test_database.py
│   ├── test_health_checker.py
│   ├── test_ssl_checker.py
│   ├── test_url_utils.py
│   └── test_website_service.py
├── docs/                        # Documentation
│   └── screenshots/
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
├── README.md                    # This file
├── CONTRIBUTING.md              # Contribution guidelines
├── PROJECT_SUMMARY.md           # Detailed project summary
├── requirements.txt             # Python dependencies
└── pyproject.toml              # Package configuration
```

## 💾 Data Storage

SitePulse stores all data locally in an SQLite database. No data is sent to external servers or cloud services.

**Database Location:**
- **Windows:** `%LOCALAPPDATA%\SitePulse\sitepulse.db`
- **Linux:** `~/.local/share/SitePulse/sitepulse.db`
- **macOS:** `~/Library/Application Support/SitePulse/sitepulse.db`

The database is created automatically on first launch.

## 🧪 Running Tests

SitePulse includes a comprehensive test suite with 70 tests covering all core functionality.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=sitepulse tests/

# Run specific test file
pytest tests/test_health_checker.py -v
```

**Test Coverage:**
- ✅ Database operations (3 tests)
- ✅ URL utilities (24 tests)
- ✅ Health checker (13 tests)
- ✅ SSL checker (10 tests)
- ✅ Website service (20 tests)

## 🔒 Security Features

SitePulse includes multiple security measures:

### URL Validation
- Only HTTP/HTTPS schemes allowed
- Private IP address blocking (RFC 1918)
- Localhost blocking
- Cloud metadata endpoint protection
- Link-local address blocking

### SSL/TLS
- Certificate verification enabled by default
- No certificate bypass options
- Hostname verification enforced

### Network Safety
- Maximum 5 redirects with validation
- HTTPS-to-HTTP downgrade prevention
- Connection timeouts
- Parameterized SQL queries (SQL injection prevention)

## ⚙️ Configuration

### Default Settings

- **Request Timeout:** 10 seconds
- **Max Redirects:** 5
- **SSL Certificate Check:** Enabled
- **User Agent:** `SitePulse/1.0 (Website Health Monitor)`

### Customizing Checks

You can customize check behavior by modifying the `HealthChecker` initialization in the code:

```python
# Example: Change timeout to 5 seconds
health_checker = HealthChecker(timeout=5, check_ssl=True)
```

## 🐛 Troubleshooting

### Issue: "tkinter not found"
**Solution:** Install tkinter for your system:
- **Ubuntu/Debian:** `sudo apt-get install python3-tk`
- **Fedora:** `sudo dnf install python3-tkinter`
- **macOS:** Tkinter is included with Python from python.org
- **Windows:** Tkinter is included with Python installer

### Issue: "Database is locked"
**Solution:** Close any other SitePulse instances. Only one instance should run at a time.

### Issue: "SSL verification failed"
**Solution:** This is expected for websites with invalid SSL certificates. The error message will provide details.

### Issue: Permission denied on Linux/macOS
**Solution:** Ensure you have write permissions to the data directory:
```bash
chmod -R u+w ~/.local/share/SitePulse/
```

## 🚦 Known Limitations

1. **Response Time:** Represents HTTP request duration, not full page rendering
2. **Availability Metrics:** Calculated from recorded checks, not continuous monitoring
3. **SSL Checks:** Only for HTTPS URLs
4. **Concurrency:** Checks run sequentially (one at a time in batch operations)
5. **Network Security:** URL validation provides basic protection but is not immune to DNS rebinding

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Clone your fork
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Write/update tests
6. Ensure all tests pass: `pytest`
7. Commit: `git commit -m "Add your feature"`
8. Push: `git push origin feature/your-feature-name`
9. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings to functions and classes
- Keep functions focused and simple
- Write tests for new features

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python 3.11+
- GUI powered by Tkinter
- HTTP requests via `requests` library
- Testing with `pytest`
- Cross-platform path handling with `pathlib`

## 📞 Support

For issues, questions, or suggestions:
- 🐛 [Open an Issue](https://github.com/Syedk07/Website-Health-Checker/issues)
- 💬 [Discussions](https://github.com/Syedk07/Website-Health-Checker/discussions)
- 📧 Email: syedk07@gmail.com

## 🗺️ Roadmap

Future enhancements being considered:

- [ ] Scheduled automatic checks
- [ ] Email/notification alerts
- [ ] Custom check intervals per website
- [ ] Performance graphs and charts
- [ ] Dark mode theme
- [ ] Multi-language support
- [ ] Database backup/restore
- [ ] Browser extension
- [ ] REST API

## ⭐ Star History

If you find SitePulse useful, please consider giving it a star on GitHub!

---

**Made with ❤️ by [Syedk07](https://github.com/Syedk07)**

**Version:** 1.0.0 | **Status:** Production Ready ✅
