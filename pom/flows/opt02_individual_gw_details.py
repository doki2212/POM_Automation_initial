import time, os
from pom.pages.home_page import HomePage
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta



GW_LIST_TAB_XPATH = "//*[@id='root']/div/aside/div/div[2]/ul/li[4]/span/a"
GW_SERIAL_INPUT_CANDIDATES = [
    "//*[@id='rc-tabs-0-panel-1']/div[2]/div/div/div/div/div/div[1]/table/thead/tr/th[1]/div[2]/span/input",
    "//*[@id='rc-tabs-0-panel-1']/div[2]/div/div/div/div/div/div[1]/table/thead/tr/th[1]/div[2]/span",
    "//*[@id='rc-tabs-2-panel-1']/div[2]/div/div/div/div/div/div[1]/table/thead/tr/th[1]/div[2]/span/input",
    "//*[@id='rc-tabs-2-panel-1']/div[2]/div/div/div/div/div/div[1]/table/thead/tr/th[1]/div[2]/span",
]
GW_OPTION_SELECT_XPATH = "//*[@id='rc-tabs-0-panel-1']/div[2]/div/div/div/div/div/div[2]/table/tbody/tr[2]/td[1]"
KPI_PAGE_XPATH = "/html/body/div[1]/div/div/main/div/div/div[1]/div[1]/div/div[8]/div"
DEVICE_LIST_TAB_XPATH = "//*[@id='root']/div/aside/div/div[2]/ul/li[5]/span/a"
DEVICES_SERIAL_INPUT_CANDIDATES = [
    "//*[@id='root']/div/div/main/div/div[2]/div/div/div/div/div/div[1]/table/thead/tr/th[1]/div[2]/span/input",
    "//*[@id='root']/div/div/main/div/div[2]/div/div/div/div/div/div[1]/table/thead/tr/th[1]/div[2]/span",
]
DEVICES_DWNLD_XPATH = "//*[@id='root']/div/div/main/div/div[1]/button"
DOWNLOAD_AS_EXCEL_CANDIDATES = [
    "//a[normalize-space()='Download as Excel']",
    "//*[@role='menu' or @role='listbox']//*[self::a or self::button or @role='menuitem'][normalize-space()='Download as Excel']",
    "//*[@role='menu' or @role='listbox']//*[self::a or self::button][normalize-space()='Download as Excel']",
    "//*[@id=':r25:']//*[self::a or self::button][normalize-space()='Download as Excel']",
]
BELL_CANDIDATES = [
    "//*[@id='root']/div/div/header/div/div[2]/div[1]/span",        # parent
    "//*[@id='root']/div/div/header/div/div[2]/div[1]/span/svg",    # child
]
#DWNLDED_FILE_XPATH = ""


class Opt02IndividualGWDetailsFlow:
    Name = "02 - Smoke test Individual GW Details"
    
    def __init__(self, driver, cfg):
        self.driver = driver
        self.cfg = cfg
        self.page = HomePage(driver, cfg)
        self.serial = None
        
    def run(self, serial: str | None = None) -> bool:
        try:
            serial = input("Enter gateway serial number ").strip()
        except EOFError:
            serial = ""
            
        if not serial:
            print("Serial Number either incorrect or not entered. Aborting")
            return False
        
        self.serial = serial
        print(f"Received Serial: {serial}")
        
        xp_tab = self._first_visible([GW_LIST_TAB_XPATH], in_iframes=False)
        if not xp_tab or not self._robust_click(xp_tab):
            print("Gateway List tab is not yet visible")
            return False
        time.sleep(10)
        xp_input = self._first_clickable(
            [xp for xp in GW_SERIAL_INPUT_CANDIDATES if xp.endswith("/input")],
            timeout=15
        ) or self._first_clickable(
            [xp for xp in GW_SERIAL_INPUT_CANDIDATES if xp.endswith("/span")],
            timeout=15
        )
        
        if not xp_input:
            print("Serial Input tab is not clickable")
            return False
        
        if not self._robust_click(xp_input):
            print("Serial Input tab could not be selected")
            return False
        
        input_xp = xp_input if xp_input.endswith("/input") else xp_input + "/input"
        
        self.page.type_xpath(input_xp, self.serial, clear=True)
        
        time.sleep(3)
    
        option_xp = self._first_visible([GW_OPTION_SELECT_XPATH], in_iframes=False)
        if not option_xp:
            print("[opt2] GW option cell did not become visible")
            return False
        
        if not self._robust_click(option_xp):
            print("[opt2] Could not click GW option cell")
            return False
        
        kpi_xp = self._first_visible([KPI_PAGE_XPATH], in_iframes=False)
        if not kpi_xp:
            print("KPI tab is not visible")
            return False
        if not self._robust_click(kpi_xp):
            print("KPI tab not clickable")
            return False
        
        time.sleep(3)
        save_dir = r"C:\Users\chriso.christudhas\OneDrive - Reliance Corporate IT Park Limited\Desktop\DAM_DOWNLOAD\KPI_SS"
        self._save_screenshot(save_dir, prefix="kpi")
        
        device_tab_xp = self._first_visible([DEVICE_LIST_TAB_XPATH], in_iframes=False)
        if not device_tab_xp:
            print("Device tab not visible")
            return False
        
        if not self._robust_click(device_tab_xp):
            print("Device tab not clickable")
            return False
        
        xp_dev_input = self._first_clickable(
            [xp for xp in DEVICES_SERIAL_INPUT_CANDIDATES if xp.endswith("/input")],
            timeout=15
        ) or self._first_clickable(
            [xp for xp in DEVICES_SERIAL_INPUT_CANDIDATES if xp.endswith("/span")],
            timeout=15
        )

        if not xp_dev_input:
            print("Device serial field not clickable")
            return False
        
        # Focus field (works for both span and input)
        if not self._robust_click(xp_dev_input):
            print("Device serial field could not be focused")
            return False
        dev_input_xp = xp_dev_input if xp_dev_input.endswith("/input") else xp_dev_input + "/input"
        self.page.type_xpath(dev_input_xp, self.serial, clear=True)
        time.sleep(3) 

        dwn_btn_xp = self._first_clickable([DEVICES_DWNLD_XPATH], timeout=self.cfg.EXPLICIT_WAIT)
        if not dwn_btn_xp:
            print("Download button not clickable")
            return False

        if not self._robust_click(dwn_btn_xp):
            print("Download button click failed")
            return False
        
        ## Click by Excel
        excel_opt_xp = self._first_clickable(DOWNLOAD_AS_EXCEL_CANDIDATES, timeout=self.cfg.EXPLICIT_WAIT)
        if excel_opt_xp:
            if not self._robust_click(excel_opt_xp):
                print("Could not click 'Download as Excel'")
                return False
        else:
            # Last-resort: CSS by the dynamic id (note the escaped colons)
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, "#\\:r25\\: a, #\\:r25\\: button")
                self.driver.execute_script("arguments[0].click()", el)
            except Exception:
                print("'Download as Excel' option not found")
                return False
            
        click_t = datetime.now()
        
        def name_variants(dt: datetime) -> list[str]:
            date = dt.strftime('%d_%m_%Y')
            hh    = dt.strftime('%I')                 # 01..12
            hh_nz = hh.lstrip('0') or '0'             # 1..12
            mm    = dt.strftime('%M')
            ampm  = dt.strftime('%p')                 # AM/PM
            # cover: zero-padded/non-padded hour + with/without space before AM/PM + case
            variants = [
                f"devices-excel_{date}_{hh}_{mm}{ampm}",
                f"devices-excel_{date}_{hh}_{mm} {ampm}",
                f"devices-excel_{date}_{hh_nz}_{mm}{ampm}",
                f"devices-excel_{date}_{hh_nz}_{mm} {ampm}",
            ]
            # preserve order but dedupe
            seen = set()
            out = []
            for v in variants:
                if v not in seen:
                    out.append(v); seen.add(v)
            return out

        expected_names = []
        for m in (0, 1, 2, -1):  # now..2 minutes back and +1 minute
            expected_names += name_variants(click_t - timedelta(minutes=m))
        # final de-dupe preserving order
        expected_names = list(dict.fromkeys(expected_names))
        print("[opt2] expected_names:", expected_names, flush=True)
        print("expected names:",expected_names, flush=True)
        ## BELL PLEASE
        bell_xp = self._first_clickable(BELL_CANDIDATES, timeout=self.cfg.EXPLICIT_WAIT)
        if not bell_xp:
            print("Bell button not visible/clickable")
            return False
        if not self._robust_click(bell_xp):
            print("Bell button could not be clicked")
            return False
        time.sleep(4)
        
        
        panel_root = self._first_visible([
            "//*[@role='dialog']",
            "//*[contains(@class,'ant-drawer')]",
            "//*[contains(@class,'ant-modal')]",
        ], in_iframes=False)

        if not panel_root:
            print("[opt2] No downloads panel became visible.", flush=True)
            return False
        
        dialog_scope = "//*[@role='dialog' or contains(@class,'ant-modal') or contains(@class,'ant-drawer')]"
        file_button_candidates = []
        for name in expected_names:
            file_button_candidates.extend([
                # list item/container → first button inside (exact)
                f"{dialog_scope}//*[normalize-space(.)='{name}']"
                f"/ancestor::*[contains(@class,'ant-list-item') or contains(@class,'ant-row') or contains(@class,'ant-space')][1]//button[1]",

                # list item/container → first button inside (contains)
                f"{dialog_scope}//*[contains(normalize-space(.),'{name}')]"
                f"/ancestor::*[contains(@class,'ant-list-item') or contains(@class,'ant-row') or contains(@class,'ant-space')][1]//button[1]",

                # button wraps the text (exact / contains)
                f"{dialog_scope}//button[.//span[normalize-space(.)='{name}']]",
                f"{dialog_scope}//button[.//*[contains(normalize-space(.),'{name}')]]",

                # text span followed by nearest button (exact / contains)
                f"{dialog_scope}//span[normalize-space(.)='{name}']/following::button[1]",
                f"{dialog_scope}//*[contains(normalize-space(.),'{name}')]/following::button[1]",

                # page-level fallbacks
                f"//button[.//span[normalize-space(.)='{name}']]",
                f"//button[.//*[contains(normalize-space(.),'{name}')]]",
                f"//span[normalize-space(.)='{name}']/following::button[1]",
                f"//*[contains(normalize-space(.),'{name}')]/following::button[1]",
            ])
            
        downloaded_btn_xp = None
        deadline = time.time() + 30
        while time.time() < deadline and not downloaded_btn_xp:
            downloaded_btn_xp = self._first_clickable(file_button_candidates, timeout=2)
            if not downloaded_btn_xp:
                time.sleep(0.5)
        
        if not downloaded_btn_xp:
            file_link_candidates = []
            for name in expected_names:
                file_link_candidates.extend([
                    # direct clickable name inside a button or anchor (dialog-scoped first)
                    f"{dialog_scope}//button[.//span[normalize-space(.)='{name}']]",
                    f"{dialog_scope}//a[normalize-space(.)='{name}']",
                    f"{dialog_scope}//a[.//*[normalize-space(.)='{name}']]",
                    # contains() fallbacks
                    f"{dialog_scope}//button[.//*[contains(normalize-space(.),'{name}')]]",
                    f"{dialog_scope}//a[contains(normalize-space(.),'{name}')]",
                    # page-level fallbacks
                    f"//button[.//span[normalize-space(.)='{name}']]",
                    f"//button[.//*[contains(normalize-space(.),'{name}')]]",
                    f"//a[normalize-space(.)='{name}']",
                    f"//a[contains(normalize-space(.),'{name}')]",
                    # as a last resort: click the text span itself
                    f"{dialog_scope}//span[normalize-space(.)='{name}']",
                    f"{dialog_scope}//*[contains(normalize-space(.),'{name}')]",
                ])
            downloaded_btn_xp = self._first_clickable(file_link_candidates, timeout=5)

        if not downloaded_btn_xp:
            print(f"[opt2] File not visible/clickable by name (tried: {expected_names}).")
            return False

        print(f"[opt2] Clicking file entry/button: {downloaded_btn_xp}", flush=True)

        # Try our robust click first
        if not self._robust_click(downloaded_btn_xp):
            # Hard fallback: JS-click the resolved element directly
            try:
                xp = downloaded_btn_xp.split(']::', 1)[1] if downloaded_btn_xp.startswith("frame[") else downloaded_btn_xp
                el = self.driver.find_element(By.XPATH, xp)
                self.driver.execute_script("arguments[0].click()", el)
            except Exception as e:
                print(f"[opt2] Final click fallback failed: {e}")
                return False     
        
        
        time.sleep(10)
        return True
    
    ## Helpers
    def _wait_any(self, xpaths, timeout: int):
    #"""Wait until any one of the given xpaths is visible; return the first that appears."""
        last = None
        for xp in xpaths:
            try:
                self.page.visible_xpath(xp, timeout=timeout)
                return xp
            except Exception as e:
                last = e
        raise last if last else TimeoutException("No candidate became visible")

    def _first_visible(self, candidates, in_iframes: bool) -> str | None:
    #"""Return first xpath that is visible; optionally search inside iframes."""
    # default content first
        for xp in candidates:
            if self._visible(xp):
                return xp
        if not in_iframes:
            return None
        # then try each frame
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

    def _visible(self, xpath: str, timeout: int = 6) -> bool:
        """Quick probe for visibility with a short timeout."""
        try:
            self.page.visible_xpath(xpath, timeout=timeout)
            return True
        except Exception:
            return False

    def _first_clickable(self, candidates, timeout: int) -> str | None:
        """Return first xpath that becomes clickable within timeout (checked per-candidate)."""
        for xp in candidates:
            try:
                self.page.clickable_xpath(xp, timeout=timeout)
                return xp
            except Exception:
                continue
        return None

    def _robust_click(self, target: str) -> bool:
        """Click an element; supports frame markers like 'frame[i]:://xpath' and JS fallback."""
        if target.startswith("frame["):
            idx = int(target.split("]::")[0].split("[")[1])
            xp  = target.split("]::", 1)[1]
            try:
                frames = self.driver.find_elements(By.XPATH, "//iframe|//frame")
                fr = frames[idx]
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
        """Try normal click; on failure, scroll then JS click."""
        try:
            self.page.click_xpath(xpath, timeout=self.cfg.EXPLICIT_WAIT)
            return True
        except (TimeoutException, StaleElementReferenceException, Exception):
            try:
                self.page.scroll_into_view(xpath)
            except Exception:
                pass
            try:
                self.page.js_click(xpath, timeout=self.cfg.EXPLICIT_WAIT)
                return True
            except Exception:
                return False
            
    def _save_screenshot(self, directory: str, prefix: str = "kpi") -> str:
        os.makedirs(directory, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        serial_part = f"_{self.serial}" if getattr(self, "serial", None) else ""
        path = os.path.join(directory, f"{prefix}{serial_part}_{ts}.png")
        self.driver.save_screenshot(path)
        print(f"[opt2] KPI screenshot saved to: {path}")
        return path