from typing import List

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# TODP consider lowering this default retry-count + allowing env variable override
def make_http_session(
    total_retry: int = 8,
    backoff_factor: float = 0.4,
    status_forcelist: List = [500, 502, 503, 504, 429],
) -> Session:
    """Create a requests session with retry logic"""
    session = Session()
    retry = Retry(
        total=total_retry,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session
