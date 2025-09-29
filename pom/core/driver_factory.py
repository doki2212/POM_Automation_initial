import os
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
## Driver settings and additional control
def create_driver(
    browser: str = "chrome",
    headless: bool = False,
    download_dir: Optional[str] = None,
    ):
    if browser.lower() != "chrome":
        raise ValueError("Only Chrome supported by this project.")
    opts = ChromeOptions()
    
    if headless:
        opts.add_argument("--headless=new")
        
        opts.add_argument("--window-size=1920,1080")
    else:
        opts.add_argument("--start-maximized")
        
    if download_dir is None:
        download_dir = os.getenv("DOWNLOAD_DIR")
    
    if download_dir:
        os.makedirs(download_dir, exist_ok= True)
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
        }
        opts.add_experimental_option("prefs", prefs)
    
    opts.add_experimental_option("excludeSwitches",["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    
    return webdriver.Chrome(options=opts)