# Ford AsBuilt Downloader

This tool automates the process of downloading Ford Motorcraft AsBuilt files using Selenium to control a Chrome browser and solve CAPTCHAs with EasyOCR.
CAPTCHAs have a solve rate of around 60% and may require multiple attempts (automatically handled).

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed
- Internet connection

## Installation

### 1. Clone or download this repository

### 2. Create a Python Virtual Environment

**Windows:**
```
python -m venv venv
```

**macOS/Linux:**
```
python3 -m venv venv
```

### 3. Activate the virtual environment

**Windows:**
```
.\venv\Scripts\activate
```

**macOS/Linux:**
```
source venv/bin/activate
```

### 4. Install required packages
```
pip install -r requirements.txt
```

## Usage

Create a text file with one VIN per line.

Run the script:
```
python asbuilt_downloader.py <path_to_vins.txt>
```

Press `Ctrl+C` to stop the script at any time and wait a moment for the process to terminate gracefully.

The tool will:
1. Process each VIN in the specified VIN file
2. Skip VINs that have already been downloaded
3. Open an automated Chrome browser session
4. Navigate to the Ford Motorcraft AsBuilt website
5. Handle country/language selection if needed (US/English)
6. Enter the VIN
7. Automatically solve the CAPTCHA using EasyOCR (with up to 5 retry attempts)
8. Submit the form and download the AsBuilt file
9. Save the file to an "asbuilt_downloads" folder named as <VIN>.ab
10. Close the browser session after processing all VINs

## Notes

- The tool creates a log file (download_results.log) tracking successes, failures, and skips (if the file already exists)
- CAPTCHA recognition may require multiple attempts
- Files are downloaded to the "asbuilt_downloads" folder in the current directory
- The tool is optimized to maintain a single browser session for all VINs

## Disclaimer and Legal Considerations

**IMPORTANT: This tool is created for educational and informational purposes only.**

- This script is intended to demonstrate web automation techniques and OCR technology in a practical context.
- Using automated tools to access websites may violate the Ford Motorcraft Service website's Terms of Service.
- The creator of this tool does not encourage or condone any use that violates terms of service, licensing agreements, or applicable laws.
- Users of this tool bear sole responsibility for ensuring their use complies with all relevant terms, conditions, and laws.
- The creator assumes no liability for any consequences arising from the use or misuse of this tool.
- This tool should only be used with legitimate access rights to Ford Motorcraft Service resources.
- Always check and respect the terms of service of any website before using automated tools.

By using this tool, you acknowledge that you understand these limitations and agree to use it responsibly and legally.

## License

Please refer to the [LICENSE](LICENSE) file for information about the license under which this tool is distributed.
