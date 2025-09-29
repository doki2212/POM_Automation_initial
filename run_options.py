# run_options.py
import sys
import argparse
import importlib

from pom.config import Config
from pom.core.driver_factory import create_driver
from pom.pages.login_page import LoginPage


#Actual Mapping of flows
FLOW_MAP = {
    # 1) All GW Details
    "1": ("pom.flows.opt01_all_gw_details", "Opt01AllGWDetailsFlow"),
    "all": ("pom.flows.opt01_all_gw_details", "Opt01AllGWDetailsFlow"),
    "all-gw": ("pom.flows.opt01_all_gw_details", "Opt01AllGWDetailsFlow"),

    # 2) Individual GW Details 
    "2": ("pom.flows.opt02_individual_gw_details", "Opt02IndividualGWDetailsFlow"),
    "ind": ("pom.flows.opt02_individual_gw_details", "Opt02IndividualGWDetailsFlow"),
    "individual": ("pom.flows.opt02_individual_gw_details", "Opt02IndividualGWDetailsFlow"),

    # 3) Tagged GW Details
    "3": ("pom.flows.opt03_tagged_gw_details", "Opt03TaggedGWDetailsFlow"),
    "tag": ("pom.flows.opt03_tagged_gw_details", "Opt03TaggedGWDetailsFlow"),
    "tagged": ("pom.flows.opt03_tagged_gw_details", "Opt03TaggedGWDetailsFlow"),

    # 4) Monitoring Summary
    "4": ("pom.flows.opt04_monitoring_summary", "Opt04MonitoringSummaryFlow"),
    "mon": ("pom.flows.opt04_monitoring_summary", "Opt04MonitoringSummaryFlow"),
    "monitoring": ("pom.flows.opt04_monitoring_summary", "Opt04MonitoringSummaryFlow"),
}

## What to pass to the run_options code
def parse_args():
    ap = argparse.ArgumentParser(description="Run a selected flow after login.")
    ap.add_argument(
        "--option",
        default=None,
        help="Which option to run (1-4 or alias). If omitted, you will be prompted."
    )
    ap.add_argument("--headless", default="false", help="Run headless? true/false (default: false)")
    ap.add_argument("--screenshot-dir", default=None, help="Optional: where to save the login screenshot")
    return ap.parse_args()


def prompt_for_option() -> str:
    print("\nSelect an option to run:")
    print("  1) All GW Details")
    print("  2) Individual GW Details (devices excel)")
    print("  3) Tagged GW Details")
    print("  4) Monitoring Summary")
    choice = input("Enter option (1-4, or alias): ").strip().lower()
    return choice


def resolve_flow_key(raw: str | None) -> str:
    if not raw:
        return prompt_for_option()
    return raw.strip().lower()


def load_flow(flow_key: str, driver, cfg):
    if flow_key not in FLOW_MAP:
        raise ValueError(
            f"Unknown option '{flow_key}'. "
            f"Valid options: {', '.join(sorted(set(k for k in FLOW_MAP if k.isdigit())))} "
            f"or aliases: {', '.join(sorted(set(k for k in FLOW_MAP if not k.isdigit())))}"
        )
    module_path, class_name = FLOW_MAP[flow_key]
    mod = importlib.import_module(module_path)
    FlowClass = getattr(mod, class_name)
    return FlowClass(driver, cfg)


def main():
    args = parse_args()
    cfg = Config()
    headless = str(args.headless).lower() in ("1", "true", "yes", "y")

    driver = create_driver(headless=headless)
    driver.implicitly_wait(cfg.IMPLICIT_WAIT)  # keep explicit waits in your BasePage

    try:
        # 1) Login
        LoginPage(driver, cfg).login_with_env(screenshot_dir=args.screenshot_dir)

        # 2) Resolve which flow to run
        key = resolve_flow_key(args.option)
        flow = load_flow(key, driver, cfg)

        # 3) Run it
        ok = flow.run()

        # 4) Exit code & message
        # If your framework prints "Smoke test passed" elsewhere, this keeps CLI truthful.
        print(f"[Flow: {flow.Name}] {'PASS' if ok else 'FAIL'}", flush=True)
        return 0 if ok else 1

    except KeyboardInterrupt:
        print("\nAborted by user.")
        return 130
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return 1
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
