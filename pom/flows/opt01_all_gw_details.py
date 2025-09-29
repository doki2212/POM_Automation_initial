# pom/flows/opt01_all_gw_details.py
import time, os
from pom.pages.home_page import HomePage
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from datetime import datetime, timedelta

GATEWAY_LIST_TAB_XPATH = os.getenv(
    "GATEWAY_LIST_TAB_XPATH",
    "//*[@id='root']/div/aside/div/div[2]/ul/li[4]/span/a"
)

PANEL_XPATHS = [
    "//*[@id='rc-tabs-1-panel-1']",
    "//*[@id='rc-tabs-0-panel-1']",
]

# Prefer clicking the BUTTON itself
DOWNLOAD_BUTTON_CANDIDATES = [
    "//*[@id='rc-tabs-1-panel-1']/div[1]/div[2]/button",
    "//*[@id='rc-tabs-0-panel-1']/div[1]/div[2]/button",
    "//*[starts-with(@id,'rc-tabs-') and contains(@id,'-panel-1')]//button[.//span or .//*[name()='svg']]",
    "(//*[name()='svg' and contains(@class,'download')])[1]/ancestor::button[1]",
    "//*[starts-with(@id,'rc-tabs-') and contains(@id,'-panel-1')]//button[.//span[contains(normalize-space(.),'Download')]]",
]

##Notification Bell XPATH
NOTIF_PARENT_XPATH = "//*[@id='root']/div/div/header/div/div[2]/div[1]/span"
NOTIF_CHILD_SVG_XPATH = "//*[@id='root']/div/div/header/div/div[2]/div[1]/span/svg"

class Opt01AllGWDetailsFlow:
    Name = "01 - All GW Details (robust)"

    def __init__(self, driver, cfg):
        self.driver = driver
        self.cfg = cfg
        self.page = HomePage(driver, cfg)

    def run(self) -> bool:
        p = self.page

        # 1) Open Gateway List tab
        try:
            p.visible_xpath(GATEWAY_LIST_TAB_XPATH, timeout=self.cfg.EXPLICIT_WAIT)
            p.click_xpath(GATEWAY_LIST_TAB_XPATH, timeout=self.cfg.EXPLICIT_WAIT)
        except Exception:
            try: p.scroll_into_view(GATEWAY_LIST_TAB_XPATH)
            except Exception: pass
            p.js_click(GATEWAY_LIST_TAB_XPATH, timeout=self.cfg.EXPLICIT_WAIT)

        # 2) Wait for *any* panel to be visible
        self._wait_any(PANEL_XPATHS, timeout=self.cfg.EXPLICIT_WAIT)

        # 3) Find a clickable DOWNLOAD button (default context, then iframes)
        btn_xpath = self._first_visible(DOWNLOAD_BUTTON_CANDIDATES, in_iframes=True)
        if not btn_xpath:
            print("[opt1] No download button became visible in page or iframes.")
            return False

        # Click robustly
        if not self._robust_click(btn_xpath):
            print(f"[opt1] Click failed for: {btn_xpath}")
            return False
        
        click_t = datetime.now()
        def make_name(dt: datetime) -> str:
            return f"gateway_list_{dt.strftime('%d_%m_%Y_%I_%M%p')}"

        base = [make_name(click_t - timedelta(minutes=m)) for m in (0, 1, 2, -1)]
        expected_names = list(dict.fromkeys(base + [n[:-2] + n[-2:].lower() for n in base]))
        
        # 4) Click Notification button
        self.driver.switch_to.default_content()
        notif_xpath = self._first_visible([NOTIF_PARENT_XPATH, NOTIF_CHILD_SVG_XPATH], in_iframes=False)
        if not notif_xpath or not self._robust_click(notif_xpath):
            return False  
        time.sleep(8)
        
        file_xpaths = []
        for name in expected_names:
            file_xpaths.extend([
                # clickable wrappers first
                f"//*[@role='dialog' or contains(@class,'ant-modal') or contains(@class,'ant-drawer')]"
                f"//button[.//span[normalize-space(.)='{name}']]",
                f"//*[@role='dialog' or contains(@class,'ant-modal') or contains(@class,'ant-drawer')]"
                f"//a[normalize-space(.)='{name}']",
                # then bare spans
                f"//*[@role='dialog' or contains(@class,'ant-modal') or contains(@class,'ant-drawer')]"
                f"//span[normalize-space(.)='{name}']",
                f"//button[.//span[normalize-space(.)='{name}']]",  # page-level fallback
                f"//span[normalize-space(.)='{name}']",
            ])
            
        downloaded_file_xpath = self._first_clickable(file_xpaths, timeout=15)
        
        if not downloaded_file_xpath:
            downloaded_file_xpath = self._first_clickable([
                "((//*[@role='dialog' or contains(@class,'ant-modal') or contains(@class,'ant-drawer')]"
                "//span[starts-with(normalize-space(.),'gateway_list_')]))[1]",
                "(//span[starts-with(normalize-space(.),'gateway_list_')])[1]"
            ], timeout=5)
            
        if not downloaded_file_xpath:
            print(f"[opt1] File not visible by name (tried: {expected_names}).")
            return False

        if not self._robust_click(downloaded_file_xpath):
            print("[opt1] Could not click the file entry.")
            return False
        
        time.sleep(10)
        return True

    # Helpers, which are a bit more.... refined? All helpers from base page did not work as intended
    def _wait_any(self, xpaths, timeout):
        last = None
        for xp in xpaths:
            try:
                self.page.visible_xpath(xp, timeout=timeout)
                return xp
            except Exception as e:
                last = e
        raise last if last else TimeoutException("No panel became visible")

    def _first_visible(self, candidates, in_iframes: bool) -> str | None:
        # Try in default content
        for xp in candidates:
            if self._visible(xp):
                return xp
        if not in_iframes:
            return None
        # Try in each iframe
        frames = self.driver.find_elements("xpath", "//iframe|//frame")
        for idx, fr in enumerate(frames):
            try:
                self.driver.switch_to.frame(fr)
                for xp in candidates:
                    if self._visible(xp):
                        # Remember we’re in this frame for click; store index marker
                        return f"frame[{idx}]::{xp}"
            except Exception:
                pass
            finally:
                self.driver.switch_to.default_content()
        return None

    def _visible(self, xpath: str) -> bool:
        try:
            self.page.visible_xpath(xpath, timeout=2)
            return True
        except Exception:
            return False

    def _robust_click(self, target: str) -> bool:
        # If target is "frame[i]::xpath", switch in, click, switch back
        if target.startswith("frame["):
            idx = int(target.split("]::")[0].split("[")[1])
            xp  = target.split("]::", 1)[1]
            try:
                fr = self.driver.find_elements("xpath", "//iframe|//frame")[idx]
            except Exception:
                return False
            try:
                self.driver.switch_to.frame(fr)
                return self._click_now(xp)
            finally:
                self.driver.switch_to.default_content()
        else:
            return self._click_now(target)

    def _click_now(self, xpath: str) -> bool:
        p = self.page
        try:
            p.click_xpath(xpath, timeout=self.cfg.EXPLICIT_WAIT)
            return True
        except (TimeoutException, StaleElementReferenceException, Exception):
            try: p.scroll_into_view(xpath)
            except Exception: pass
            try:
                p.js_click(xpath, timeout=self.cfg.EXPLICIT_WAIT)
                return True
            except Exception:
                return False
            
    def _first_clickable(self, candidates, timeout: int) -> str | None:
        for xp in candidates:
            try:
                self.page.clickable_xpath(xp,timeout = timeout)
                return xp
            except Exception:
                continue
        return None
