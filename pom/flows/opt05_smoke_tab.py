import time, os
from pom.pages.home_page import HomePage
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta

GATEWAY_LIST_TAB_XPATH = os.getenv(
    "GATEWAY_LIST_TAB_XPATH",
    "//*[@id='root']/div/aside/div/div[2]/ul/li[4]/span/a"
)

#TAG_TAB_XPATH = "//*[@id='rc-tabs-0-panel-1']/div[1]/div[1]/div/span/div"
TAG_TAB_CANDIDATES = [
    "//*[@id='rc-tabs-0-panel-1']/div[1]/div[1]/div/span/div",   # old
    "//*[@id='rc-tabs-7-panel-1']/div[1]/div[1]/div/div",        # new
    # sensible fallbacks (Ant Design select container/selector inside the active panel)
    "//*[starts-with(@id,'rc-tabs-') and contains(@id,'-panel-1')]//div[contains(@class,'ant-select-selector')][1]",
    "//*[starts-with(@id,'rc-tabs-') and contains(@id,'-panel-1')]//div[contains(@class,'ant-select')][1]",
]
OPEN_TAG_INPUT_XPATHS = [
    "//div[contains(@class,'ant-select') and contains(@class,'open')]//input",
    "//div[contains(@class,'ant-select-open')]//input",
    "//div[contains(@class,'ant-select-focused')]//input",
    "//div[contains(@class,'ant-select') and (contains(@class,'open') or contains(@class,'focused'))]//*[@contenteditable='true']",
    "//*[@contenteditable='true']",
]

PANEL_XPATHS = [
    "//*[@id='rc-tabs-1-panel-1']",
    "//*[@id='rc-tabs-0-panel-1']",
]


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

class Opt05SmokeTabFlow:
    Name = "03 - Tagged GW Details"

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
        
        try:
            tag_text = input("Enter tag text (e.g., 'Mumbai Zone A'): ").strip()
        except EOFError:
            tag_text = ""
        if not tag_text:
            print("[opt3] No tag text entered. Aborting.")
            return False
        
        trigger_xp = self._first_visible(TAG_TAB_CANDIDATES, in_iframes=False)
        if not trigger_xp:
            print("[opt3] Tag control not visible")
            return False

        if not self._robust_click(trigger_xp):
            print(f"[opt3] Tag control not clickable: {trigger_xp}")
            return False

        if not self._type_into_tag(trigger_xp, tag_text):
            print("[opt3] Failed to type into Tag control")
            return False

        btn_xpath = self._first_visible(DOWNLOAD_BUTTON_CANDIDATES, in_iframes=True)
        if not btn_xpath:
            print("[opt3] No download button became visible in page or iframes.")
            return False

        if not self._robust_click(btn_xpath):
            print(f"[opt3] Could not click download button: {btn_xpath}")
            return False

        self.driver.switch_to.default_content()
        notif_xpath = self._first_visible([NOTIF_CHILD_SVG_XPATH, NOTIF_PARENT_XPATH], in_iframes=False)
        if not notif_xpath:
            print("[opt3] Notification icon not visible.")
            return False

        if not self._robust_click(notif_xpath):
            print(f"[opt3] Could not click notification icon: {notif_xpath}")
            return False
        time.sleep(2)
        click_t = datetime.now()
        
        def name_variants(dt: datetime) -> list[str]:
            date  = dt.strftime('%d_%m_%Y')
            hh    = dt.strftime('%I')                 # 01..12
            hh_nz = hh.lstrip('0') or '0'             # 1..12 without leading zero
            mm    = dt.strftime('%M')
            ampm  = dt.strftime('%p')                 # AM/PM

            variants = [
                f"gateway_list_{date}_{hh}_{mm}{ampm}",
                f"gateway_list_{date}_{hh}_{mm} {ampm}",
                f"gateway_list_{date}_{hh_nz}_{mm}{ampm}",
                f"gateway_list_{date}_{hh_nz}_{mm} {ampm}",
            ]

            # optional debug:
            print("[opt3] name_variants for", dt.strftime('%H:%M'), "=>", variants, flush=True)
            return variants
        expected_names = []
        for m in (0, 1, 2, -1):  # now..2 minutes back and +1 minute
            expected_names += name_variants(click_t - timedelta(minutes=m))
        # final de-dupe preserving order
        expected_names = list(dict.fromkeys(expected_names))
        print("expected names:",expected_names, flush=True)
        print("[opt3] expected_names:", expected_names, flush=True)
        
        panel_root = self._first_visible([
            "//*[@role='dialog']",
            "//*[contains(@class,'ant-drawer')]",
            "//*[contains(@class,'ant-modal')]",
        ], in_iframes=False)
        if not panel_root:
            print("[opt3] No downloads panel became visible.")
            return False

        DIALOG_SCOPE = "//*[@role='dialog' or contains(@class,'ant-modal') or contains(@class,'ant-drawer')]"

        file_button_candidates = []
        for name in expected_names:
            file_button_candidates.extend([
                # list item/container → first button inside (exact / contains)
                f"{DIALOG_SCOPE}//*[normalize-space(.)='{name}']"
                f"/ancestor::*[contains(@class,'ant-list-item') or contains(@class,'ant-row') or contains(@class,'ant-space')][1]//button[1]",
                f"{DIALOG_SCOPE}//*[contains(normalize-space(.),'{name}')]"
                f"/ancestor::*[contains(@class,'ant-list-item') or contains(@class,'ant-row') or contains(@class,'ant-space')][1]//button[1]",

                # button/anchor wraps the filename
                f"{DIALOG_SCOPE}//button[.//span[normalize-space(.)='{name}']]",
                f"{DIALOG_SCOPE}//a[normalize-space(.)='{name}']",
                f"{DIALOG_SCOPE}//a[.//*[normalize-space(.)='{name}']]",

                # filename span followed by nearest button (exact / contains)
                f"{DIALOG_SCOPE}//span[normalize-space(.)='{name}']/following::button[1]",
                f"{DIALOG_SCOPE}//*[contains(normalize-space(.),'{name}')]/following::button[1]",

                # page-level fallbacks (just in case)
                f"//button[.//span[normalize-space(.)='{name}']]",
                f"//button[.//*[contains(normalize-space(.),'{name}')]]",
                f"//a[normalize-space(.)='{name}']",
                f"//a[contains(normalize-space(.),'{name}')]",
                f"//span[normalize-space(.)='{name}']",
                f"//*[contains(normalize-space(.),'{name}')]",
            ])
        
        downloaded_btn_xp = None
        deadline = time.time() + 30
        while time.time() < deadline and not downloaded_btn_xp:
            downloaded_btn_xp = self._first_clickable(file_button_candidates, timeout=2)
            if not downloaded_btn_xp:
                time.sleep(0.5)

        if not downloaded_btn_xp:
            print(f"[opt3] File not visible/clickable by name (tried: {expected_names}).")
            return False
        
        print(f"[opt3] Clicking file entry/button: {downloaded_btn_xp}", flush=True)
        
        if not self._robust_click(downloaded_btn_xp):
            try:
                xp = downloaded_btn_xp.split(']::', 1)[1] if downloaded_btn_xp.startswith("frame[") else downloaded_btn_xp
                el = self.driver.find_element(By.XPATH, xp)

                actionable = None
                try:
                    actionable = el.find_element(By.XPATH, "ancestor-or-self::button[1]")
                except Exception:
                    pass
                if actionable is None:
                    try:
                        actionable = el.find_element(By.XPATH, "ancestor-or-self::a[1]")
                    except Exception:
                        pass
                if actionable is None:
                    try:
                        actionable = el.find_element(By.XPATH, "ancestor::*[@role='button' or contains(@class,'ant-btn')][1]")
                    except Exception:
                        pass

                target = actionable or el
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
                self.driver.execute_script("arguments[0].click()", target)
            except Exception as e:
                print(f"[opt3] Final click fallback failed: {e}")
                return False


        time.sleep(10)
        return True
    
    
    
        # ---------- helpers ----------
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
        for xp in candidates:
            if self._visible(xp):
                return xp
        if not in_iframes:
            return None
        frames = self.driver.find_elements(By.XPATH, "//iframe|//frame")
        for idx, fr in enumerate(frames):
            try:
                self.driver.switch_to.frame(fr)
                for xp in candidates:
                    if self._visible(xp):
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
        
        
    def _type_into_tag(self, trigger_xpath: str, text: str) -> bool:
        p = self.page
        try:
            p.scroll_into_view(trigger_xpath)
        except Exception:
            pass
        if not self._robust_click(trigger_xpath):
            return False

        time.sleep(0.2)

        input_xp = self._first_clickable(OPEN_TAG_INPUT_XPATHS, timeout=5)
        el = None
        if input_xp:
            try:
                el = p.visible_xpath(input_xp, timeout=5)
            except Exception:
                el = None

        if el is None:
            try:
                el = self.driver.switch_to.active_element
            except Exception:
                el = None

        if el is None:
            print("[opt3] Could not resolve a focusable tag input.")
            return False

        try:
            el.clear()
        except Exception:
            try:
                el.send_keys(Keys.CONTROL, "a"); el.send_keys(Keys.BACKSPACE)
            except Exception:
                try:
                    el.send_keys(Keys.COMMAND, "a"); el.send_keys(Keys.BACKSPACE)
                except Exception:
                    pass

        try:
            el.send_keys(text)
            el.send_keys(Keys.ENTER)
            return True
        except Exception:
            return False