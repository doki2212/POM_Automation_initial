import os
import sys
from pom.core.driver_factory import create_driver
from pom.pages.login_page import LoginPage
from pom.config import Config

def main():
    cfg = Config()
    driver = create_driver(headless=False)          
    driver.implicitly_wait(cfg.IMPLICIT_WAIT)       
    try:
        # If you want to force a folder, pass screenshot_dir=r"...", not needed for OG PC since path is already mentioned
        screenshot_path = LoginPage(driver, cfg).login_with_env()
        size = os.path.getsize(screenshot_path) if os.path.exists(screenshot_path) else 0
        ok = os.path.isfile(screenshot_path) and size > 0

        print(f"Screenshot saved to: {screenshot_path}")
        print(f"File size: {size} bytes")
        print("LOGIN SMOKE:", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    except Exception as e:
        print("LOGIN SMOKE: ERROR:", e)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
