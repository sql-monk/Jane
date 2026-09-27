"""Jane test site: deterministic website fixture for collector and discovery tests.

from jane_testsite import serve_in_thread, expected
with serve_in_thread() as base_url:
    ...  # crawl base_url; compare with expected().sets["recursive"]
"""

from .server import make_server, serve_in_thread
from .site import expected

__all__ = ["expected", "make_server", "serve_in_thread"]
