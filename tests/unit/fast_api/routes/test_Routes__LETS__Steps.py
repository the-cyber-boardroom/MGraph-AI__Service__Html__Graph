# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__LETS__Steps - Tests for LETS step routes
# Uses in-memory cache service for testing
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                               import TestCase
from mgraph_ai_service_cache_client.client.cache_service.register_cache_service             import register_cache_service__in_memory
from mgraph_ai_service_html_graph.fast_api.routes.Routes__LETS__Steps                       import Routes__LETS__Steps
from mgraph_ai_service_html_graph.fast_api.routes.Routes__LETS__Steps                       import TAG__ROUTES_LETS
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Info              import Schema__LETS__Step__Info
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__List__Response    import Schema__LETS__Step__List__Response
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Execute__Request  import Schema__LETS__Step__Execute__Request
from mgraph_ai_service_html_graph.schemas.routes.lets.Schema__LETS__Step__Execute__Response import Schema__LETS__Step__Execute__Response
from mgraph_ai_service_html_graph.service.cache_storage.Html_Cache__Client                  import Html_Cache__Client


class test_Routes__LETS__Steps(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cache_service_client = register_cache_service__in_memory(return_client=True)
        cls.html_cache_client    = Html_Cache__Client()
        cls.routes = Routes__LETS__Steps(cache_client=cls.html_cache_client)
        cls.namespace = 'test-namespace'

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with Routes__LETS__Steps() as _:
            assert type(_)     is Routes__LETS__Steps
            assert _.tag       == TAG__ROUTES_LETS

    # ═══════════════════════════════════════════════════════════════════════════
    # Discovery Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_steps(self):
        """Test GET /lets/steps - list all steps"""
        result = self.routes.steps()

        assert type(result)  is Schema__LETS__Step__List__Response
        assert result.count  >= 3                                                # At least 3 built-in steps
        assert len(result.steps) == result.count

        # Check step info structure
        for step in result.steps:
            assert type(step)        is Schema__LETS__Step__Info
            assert step.step_type    is not None
            assert step.name         is not None
            assert step.description  is not None

    def test_steps__contains_expected_types(self):
        """Test that expected step types are present"""
        result      = self.routes.steps()
        step_types  = [step.step_type for step in result.steps]

        assert 'HTML_FROM_RAW'  in step_types
        assert 'HTML_TO_DICT'   in step_types
        assert 'DICT_TO_MGRAPH' in step_types

    def test_step__info(self):
        """Test GET /lets/steps/{step_type} - get step details"""
        result = self.routes.step__info(step_type='HTML_TO_DICT')

        assert type(result)       is Schema__LETS__Step__Info
        assert result.step_type   == 'HTML_TO_DICT'
        assert result.name        is not None
        assert result.description is not None

    def test_step__info__case_insensitive(self):
        """Test step lookup is case insensitive"""
        result = self.routes.step__info(step_type='html_to_dict')

        assert type(result)       is Schema__LETS__Step__Info
        assert result.step_type   == 'html_to_dict'

    def test_step__info__not_found(self):
        """Test 404 for unknown step type"""
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as context:
            self.routes.step__info(step_type='UNKNOWN_STEP')

        assert context.exception.status_code == 404
        assert 'NOT_FOUND' in str(context.exception.detail)

    # ═══════════════════════════════════════════════════════════════════════════
    # Stateless Execution Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_step__execute(self):
        """Test POST /lets/steps/{step_type}/execute - stateless execution"""
        request = Schema__LETS__Step__Execute__Request(input_data={'html': '<html></html>'})
        result  = self.routes.step__execute(step_type='HTML_TO_DICT', request=request)

        assert type(result)      is Schema__LETS__Step__Execute__Response
        assert result.step_type  == 'HTML_TO_DICT'
        assert result.from_cache is False                                        # Stateless = no cache

    def test_step__execute__not_found(self):
        """Test 404 for unknown step type in execute"""
        from fastapi import HTTPException

        request = Schema__LETS__Step__Execute__Request(input_data={})

        with self.assertRaises(HTTPException) as context:
            self.routes.step__execute(step_type='UNKNOWN', request=request)

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Cached Execution Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_step__status__not_found_cache(self):
        """Test 404 when cache_id doesn't exist"""
        from fastapi import HTTPException
        from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id import Cache_Id

        with self.assertRaises(HTTPException) as context:
            self.routes.step__status(namespace  = self.namespace   ,
                                     step_type  = 'HTML_TO_DICT'   ,
                                     cache_id   = Cache_Id()       )

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Method Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__get_step_class__valid(self):
        """Test _get_step_class returns correct class"""
        step_class = self.routes._get_step_class('HTML_TO_DICT')

        assert step_class is not None
        assert step_class.__name__ == 'Html_LETS__Html__To__Dict'

    def test__get_step_class__case_insensitive(self):
        """Test _get_step_class is case insensitive"""
        step_class = self.routes._get_step_class('html_to_dict')

        assert step_class is not None

    def test__get_step_class__invalid(self):
        """Test _get_step_class returns None for invalid"""
        step_class = self.routes._get_step_class('INVALID_STEP')

        assert step_class is None
