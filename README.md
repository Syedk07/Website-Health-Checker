# SitePulse

A lightweight website health monitoring and checking tool built with Python.

## Overview

SitePulse is a beginner-friendly desktop application that allows you to monitor the availability and basic technical health of websites. Track HTTP status codes, response times, SSL certificate expiration, and maintain a complete monitoring history.

## Features

- **Website Availability Checks** - Monitor if websites are reachable
- **HTTP Status Detection** - Identify response codes (200, 404, 500, etc.)
- **Response Time Measurement** - Track how quickly websites respond
- **SSL Certificate Inspection** - Check certificate validity and expiration
- **Monitoring History** - Store and review all check results
- **Health Reports** - Generate availability statistics and response time summaries
- **CSV Export** - Export monitoring data for external analysis
- **Clean Desktop Interface** - Professional dashboard built with Tkinter

## Requirements

- Python 3.11 or newer
- Windows, Linux, or macOS

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/SitePulse.git
cd SitePulse
```

### 2. Create a virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install SitePulse in development mode

```bash
pip install -e .
```

## Usage

### Launch the application

After installation, you can launch SitePulse using:

```bash
sitepulse
```

Or directly with Python:

```bash
python -m sitepulse
```

### Quick Start

1. **Add a website** - Click "Add Website" and enter a URL
2. **Run a check** - Click "Check Now" to test website health
3. **View results** - See status, response time, and SSL information
4. **Review history** - Browse past check results in the History tab
5. **Generate reports** - View availability statistics in the Reports tab

## Project Structure

```
SitePulse/
├── src/
│   └── sitepulse/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── database/
│       ├── models/
│       ├── services/
│       ├── ui/
│       └── utils/
├── tests/
├── docs/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Development

### Running Tests

```bash
pytest
```

### Running Tests with Coverage

```bash
pytest --cov=sitepulse tests/
```

## Data Storage

SitePulse stores all data locally in an SQLite database. The database is created automatically in your system's application data directory:

- **Windows:** `%LOCALAPPDATA%\SitePulse\`
- **Linux:** `~/.local/share/SitePulse/`
- **macOS:** `~/Library/Application Support/SitePulse/`

No data is sent to external servers or cloud services.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Limitations

- This tool performs basic HTTP/HTTPS availability checks and SSL certificate inspection
- Response time measurements represent HTTP request duration, not full page rendering
- Availability percentages are calculated from recorded checks, not continuous monitoring
- The application does not perform port scanning, vulnerability testing, or website crawling
- Network security relies on standard URL validation and redirect limiting

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
