# POM_Automation_initial
An attempt in making a Selenium automation framework following Page Object Model pattern which was successful, thanks to AI.
This framework is designed with two things in mind, maintainability and reusability. The UI automation is made for chrome with compatibility with other browsers to be added in the future.
---
## Features
-	Modular Page Object Model design
-	Environment-based credentials via `.env`
-	Headless mode for CI pipelines
-	Download verification tests
---
## Tech Stack
-	Language: Python 3.11-3.13
-	Architecture: Page Object Model
-	Automation: Selenium WebDriver
-	Environment Management: python-dotenv
-	Browser Drivers: webdriver-manager
---
## Project Structure
POM_Automation_initial/
│
├── pom/ # Page classes and reusable methods
├── smoke_login.py # Smoke test for login flow
├── smoke_home.py # Smoke test for home page
├── check_download_button.py # File download validation
├── run_options.py # Handles CLI args (browser, headless)
├── .env.example # Environment variable template
├── requirements.txt # Dependencies list
└── README.md # (You're reading this!)
---
## Environment Variables
-	BASE_URL – site under test (e.g., https://example.com)
-	LOGIN_USERNAME – username for login
-	LOGIN_PASSWORD – password for login
-	DEFAULT_TAB – expected landing tab after login (if your tests assert it)
-	HEADLESS – "True"/"False" to run without UI
---

## Setup Instructions
1.	Clone the repository
```bash
git clone https://github.com/doki2212/POM_Automation_initial.git
cd POM_Automation_initial
```
2.	Create a virtual environment
```
python -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate
```
3.	Install dependencies
```
pip install -r requirements.txt
```
4.	Configure environment variables
```
cp .env.example .env
```
---
## Running the tests
```
python smoke_login.py
python smoke_home.py
python check_download_button.py
```
---
## Future Add-Ons/Rectifications
-	Allure report integration if possible
-	Tagging flow option  
-	Jenkins CI/CD
-	Failure Screenshot
-	A better readme file
-	Eliminate copy of helpers
-	Compatibility with Mozilla Firefox
---
## Notes
-	Tested primarily on Google Chrome with compatibility for other browsers to be released later
-	‘.env’ file to be configured before running tests
---
## License
MIT License © 2025 doki2212
