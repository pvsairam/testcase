import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main(output_path: str):
    # Setup path so we can import core modules
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from core.config import load_config, resolve_password
    from core.logging import get_logger
    from fusion.login_page import LoginPage
    
    logger = get_logger()
    config = load_config(Path(".env"))
    password = resolve_password(config)
    
    from core.display import get_screen_resolution
    
    width, height = get_screen_resolution()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--no-sandbox",
                "--start-maximized"
            ]
        )
        context = browser.new_context(
            viewport={"width": width, "height": height}
        )
        page = context.new_page()
        
        logger.info(f"Generating auth state for {config.fusion_user}...")
        login_page = LoginPage(page, is_oracle=True)
        try:
            login_page.full_login(config.fusion_url, config.fusion_user, password)
            # Wait a moment for cookies to settle
            page.wait_for_timeout(2000)
            
            state_path = Path(output_path)
            state_path.parent.mkdir(parents=True, exist_ok=True)
            context.storage_state(path=str(state_path))
            logger.info(f"Auth state successfully saved to {state_path}")
        except Exception as e:
            logger.error(f"Failed to generate auth state: {e}")
            try:
                page.screenshot(path="generate_auth_error.png")
            except Exception as e2:
                logger.error(f"Failed to save debug screenshot: {e2}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "engine/.auth_state.json"
    main(out_path)
