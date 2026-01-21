from unittest                                                          import TestCase
from phase_e.url_fetch.Html_Fetcher                                    import Html_Fetcher
from phase_e.url_fetch.schemas.Schema__Html_Fetcher__Config            import Schema__Html_Fetcher__Config


class test_Html_Fetcher__Config(TestCase):
    """Test fetcher configuration options."""

    def test_config__custom_timeout(self):                             # Test custom timeout
        config  = Schema__Html_Fetcher__Config(timeout_seconds=5)
        fetcher = Html_Fetcher(config=config)

        assert int(fetcher.config.timeout_seconds) == 5

    def test_config__custom_retries(self):                             # Test custom retries
        config  = Schema__Html_Fetcher__Config(max_retries=5)
        fetcher = Html_Fetcher(config=config)

        assert int(fetcher.config.max_retries) == 5

    def test_config__custom_user_agent(self):                          # Test custom user agent
        config  = Schema__Html_Fetcher__Config(user_agent='Custom Agent/1.0')
        fetcher = Html_Fetcher(config=config)

        assert fetcher.config.user_agent == 'Custom Agent/1.0'

    def test_config__disable_rate_limiting(self):                      # Test disable rate limiting
        config  = Schema__Html_Fetcher__Config(min_request_interval_ms=0)
        fetcher = Html_Fetcher(config=config)

        assert int(fetcher.config.min_request_interval_ms) == 0