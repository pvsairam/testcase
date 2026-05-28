"""Oracle Fusion-specific wait utilities."""

from playwright.sync_api import Page, TimeoutError as PWTimeout
from core.logging import get_logger

logger = get_logger()

def wait_for_fusion_idle(page: Page, timeout_ms: int = 30000) -> None:
    """Wait for Oracle Fusion specific spinners and network idle."""
    slice_ms = timeout_ms // 4
    
    # 1. Network idle
    logger.debug("Waiting for network idle")
    try:
        page.wait_for_load_state("networkidle", timeout=slice_ms)
    except PWTimeout:
        pass
        
    # Spinners
    spinners = [
        "div.AFLoadingBlock:visible",
        "[aria-busy='true']:visible",
        ".AFLogo[role='progressbar']:visible",
        ".oj-progress-circle:visible",
        ".oj-conveyor-belt-item.oj-selected:visible"
    ]
    
    for spinner in spinners:
        logger.debug(f"Waiting for spinner to hide: {spinner}")
        try:
            page.locator(spinner).wait_for(state="hidden", timeout=slice_ms)
        except PWTimeout:
            pass


def wait_for_any_idle(page: Page, is_oracle: bool, timeout_ms: int = 30000) -> None:
    """Wait for application idle based on app type."""
    if is_oracle:
        wait_for_fusion_idle(page, timeout_ms)
    else:
        logger.debug("Waiting for domcontentloaded")
        page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
