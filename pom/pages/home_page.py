# pom/pages/home_page.py
import os
import importlib
from typing import Optional
from pom.core.base_page import BasePage

TAB_XPATH_T   = "//a[normalize-space(text())='{TAB}'] | //button[normalize-space(text())='{TAB}']"
OPTION_BY_TEXT = "//*[self::a or self::button or self::div][normalize-space(text())='{TXT}']"


class HomePage(BasePage):
    def __init__(self, driver, cfg):
        super().__init__(driver, cfg)
        self._auto_open_default()

    # More Helpers

    def open_tab(self, tab_name: str) -> None:
        """Open a tab by its visible label text."""
        self.click_xpath(TAB_XPATH_T.replace("{TAB}", tab_name))

    def open_tab_by_xpath(self, tab_xpath: str) -> None:
        """Open a tab by its XPath (handy for stable, app-specific locators)."""
        self._safe_click(tab_xpath)

    def select_option_by_text(self, text: str) -> None:
        self.click_xpath(OPTION_BY_TEXT.replace("{TXT}", text))

    def click_download_by_xpath(self, download_xpath: str) -> None:
        self.click_xpath(download_xpath)

    def run_options(self, option: str) -> bool:
        """Resolve the flow by option key and run it. Returns True/False from the flow."""
        Flow = self._resolve_flow(option)

        #Fall back to empty ctor.
        try:
            flow = Flow(self.driver, self.cfg)
        except TypeError:
            flow = Flow()

        #Fall back to legacy run
        try:
            return bool(flow.run())
        except TypeError:
            return bool(flow.run(self.driver, self.cfg))

    # Default

    def _auto_open_default(self) -> None:
        """
        Auto-open a default tab if configured:
        - Prefer DEFAULT_TAB_XPATH (from Config or .env)
        - Else use DEFAULT_TAB (visible text)
        """
        tab_xpath = getattr(self.cfg, "DEFAULT_TAB_XPATH", "") or os.getenv("DEFAULT_TAB_XPATH", "")
        if tab_xpath:
            self.open_tab_by_xpath(tab_xpath)
            return
        tab_text = getattr(self.cfg, "DEFAULT_TAB", "")
        if tab_text:
            self.open_tab(tab_text)

    def _safe_click(self, xpath: str, timeout: Optional[int] = None) -> None:
        """Click with visibility + JS fallback for stubborn elements."""
        try:
            self.visible_xpath(xpath, timeout or self.cfg.EXPLICIT_WAIT)
            self.click_xpath(xpath, timeout or self.cfg.EXPLICIT_WAIT)
        except Exception:
            try:
                self.scroll_into_view(xpath)
            except Exception:
                pass
            self.js_click(xpath, timeout or self.cfg.EXPLICIT_WAIT)

    def _resolve_flow(self, key: str):
        """Map user input to a flow class via dynamic import."""
        k = key.strip().lower()

        # Mapping for smoke test
        flow_map = {
            # 01
            "1": ("pom.flows.opt01_all_gw_details", "Opt01AllGWDetailsFlow"),
            "01": ("pom.flows.opt01_all_gw_details", "Opt01AllGWDetailsFlow"),
            "all": ("pom.flows.opt01_all_gw_details", "Opt01AllGWDetailsFlow"),
            "all_gw_details": ("pom.flows.opt01_all_gw_details", "Opt01AllGWDetailsFlow"),

            # 02
            "2": ("pom.flows.opt02_individual_gw_details", "Opt02IndividualGWDetailsFlow"),
            "02": ("pom.flows.opt02_individual_gw_details", "Opt02IndividualGWDetailsFlow"),
            "individual": ("pom.flows.opt02_individual_gw_details", "Opt02IndividualGWDetailsFlow"),
            "individual_gw_details": ("pom.flows.opt02_individual_gw_details", "Opt02IndividualGWDetailsFlow"),

            # 03
            "3": ("pom.flows.opt03_tagged_gw_details", "Opt03TaggedGWDetailsFlow"),
            "03": ("pom.flows.opt03_tagged_gw_details", "Opt03TaggedGWDetailsFlow"),
            "tagged": ("pom.flows.opt03_tagged_gw_details", "Opt03TaggedGWDetailsFlow"),
            "tagged_gw_details": ("pom.flows.opt03_tagged_gw_details", "Opt03TaggedGWDetailsFlow"),

            # 04
            "4": ("pom.flows.opt04_monitoring_summary", "Opt04MonitoringSummaryFlow"),
            "04": ("pom.flows.opt04_monitoring_summary", "Opt04MonitoringSummaryFlow"),
            "monitoring": ("pom.flows.opt04_monitoring_summary", "Opt04MonitoringSummaryFlow"),
            "monitoring_summary": ("pom.flows.opt04_monitoring_summary", "Opt04MonitoringSummaryFlow"),

            # 05 (smoke), not used in actual
            "5": ("pom.flows.opt05_smoke_tab", "Opt05SmokeTabFlow"),
            "05": ("pom.flows.opt05_smoke_tab", "Opt05SmokeTabFlow"),
            "smoke": ("pom.flows.opt05_smoke_tab", "Opt05SmokeTabFlow"),
            "smoke_tab": ("pom.flows.opt05_smoke_tab", "Opt05SmokeTabFlow"),
        }

        if k not in flow_map:
            raise ValueError(f"Unknown option: {key}")

        module_path, class_name = flow_map[k]
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)
