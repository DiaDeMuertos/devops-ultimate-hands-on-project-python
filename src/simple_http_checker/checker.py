import logging
import requests
from typing import Collection

logger = logging.getLogger(__name__)


def check_url(urls: Collection[str], timeout: int = 5) -> dict[str, str]:
    """
    Check a list of URLs and returns their status.

    Args:
        urls: A list of URLs strings to check.
        timeout: Maximum time in seconds to wait for each request. Deault to 5.

    Returns:
        A dictionary mapping each URL to its status string.
    """

    logger.info(f"Starting check for {len(urls)} URLs with a timeout of {timeout}")
    results: dict[str, str] = {}

    for url in urls:
        status = "UNKNOWN"

        try:
            logger.debug(f"Checking URL: {url}")
            response = requests.get(url, timeout=timeout)

            if response.ok:
                status = f"{response.status_code} OK"
            else:
                status = f"{response.status_code} {response.reason}"
        except requests.exceptions.Timeout:
            status = "TIMEOUT"
            logger.warning(f"Connection to {url} time out.")
        except requests.exceptions.ConnectionError:
            status = "CONNECTION_ERROR"
            logger.warning(f"Connection error for {url}.")
        except requests.exceptions.RequestException as e:
            status = f"REQUEST_ERROR: {type(e).__name__}"
            logger.error(f"An unexpected request error ocurred for {url}: {e}", exc_info=True)

        results[url] = status
        logger.debug(f"Checked: {url:<40} -> {status}")

    logger.info("URL check finished.")

    return results
