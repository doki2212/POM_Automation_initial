#Smoke_test by AI ## Works better than the one I made, one day
import sys, os
from pom.core.driver_factory import create_driver
from pom.pages.login_page import LoginPage
from pom.pages.home_page import HomePage
from pom.config import Config  # your layout

def main():
    cfg = Config   # or Config()
    driver = create_driver(headless=False)
    try:
        # Login first (your login returns a screenshot path)
        LoginPage(driver, cfg).login_with_env()

        # Now run the smoke flow through HomePage
        home = HomePage(driver, cfg)
        ok = home.run_options("3")  # "7"/"07"/"smoke"/"smoke_tab" all work

        print("HOME SMOKE:", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    except Exception as e:
        print("HOME SMOKE: ERROR:", e)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
