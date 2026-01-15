# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__Profiles - Tests for profile routes
# Uses in-memory cache service for testing
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                import TestCase
from fastapi                                                                                 import HTTPException
from osbot_utils.type_safe.primitives.domains.identifiers.Cache_Id                           import Cache_Id
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Execute__Request  import Schema__Profile__Execute__Cached__Request
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Profiles                           import Routes__Profiles
from mgraph_ai_service_html_graph.fast_api.routes.Routes__Profiles                           import TAG__ROUTES_PROFILES
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Info              import Schema__Profile__Info
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__List__Response    import Schema__Profile__List__Response
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Execute__Request  import Schema__Profile__Execute__Request
from mgraph_ai_service_html_graph.schemas.routes.profiles.Schema__Profile__Execute__Response import Schema__Profile__Execute__Response
from mgraph_ai_service_html_graph.utils.testing.Html_Generator__For_Tests                    import Html_Generator__For_Tests
from tests.unit.Html_Graph__Service__Fast_API__Test_Objs                                     import create_html_cache_client


class test_Routes__Profiles(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_cache_client, cls.cache_service = create_html_cache_client()
        cls.routes        = Routes__Profiles(cache_client=cls.html_cache_client)
        cls.html_gen      = Html_Generator__For_Tests()
        cls.namespace     = 'test-namespace'

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with Routes__Profiles() as _:
            assert type(_)      is Routes__Profiles
            assert _.tag        == TAG__ROUTES_PROFILES
            assert _.registry   is not None                                      # Auto-initialized

    def test__init____registry_setup(self):
        """Test registry is automatically set up with profiles"""
        routes   = Routes__Profiles()
        profiles = routes.registry.list_profiles()

        assert len(profiles) >= 2                                                # At least 2 built-in profiles

    # ═══════════════════════════════════════════════════════════════════════════
    # Discovery Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_profiles(self):
        """Test GET /profiles - list all profiles"""
        result = self.routes.profiles()

        assert type(result)  is Schema__Profile__List__Response
        assert result.count  >= 2                                                # At least 2 built-in profiles
        assert len(result.profiles) == result.count

        # Check profile info structure
        for profile in result.profiles:
            assert type(profile)        is Schema__Profile__Info
            assert profile.profile_id   is not None
            assert profile.name         is not None
            assert profile.description  is not None
            assert profile.steps        is not None
            assert isinstance(profile.steps, list)

    def test_profiles__contains_expected(self):
        """Test that expected profiles are present"""
        result      = self.routes.profiles()
        profile_ids = [str(p.profile_id) for p in result.profiles]

        assert 'html-to-dict'   in profile_ids
        assert 'html-to-mgraph' in profile_ids

    def test_profile__info(self):
        """Test GET /profiles/{profile_id} - get profile details"""
        result = self.routes.profile__info(profile_id='html-to-dict')

        assert type(result)       is Schema__Profile__Info
        assert str(result.profile_id) == 'html-to-dict'
        assert result.name        is not None
        assert result.description is not None
        assert result.steps       is not None
        assert len(result.steps)  >= 1

    def test_profile__info__html_to_mgraph(self):
        """Test html-to-mgraph profile has multiple steps"""
        result = self.routes.profile__info(profile_id='html-to-mgraph')

        assert type(result)       is Schema__Profile__Info
        assert len(result.steps)  >= 2                                           # Should have multiple steps

    def test_profile__info__not_found(self):
        """Test 404 for unknown profile"""
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as context:
            self.routes.profile__info(profile_id='unknown-profile')

        assert context.exception.status_code == 404
        assert 'NOT_FOUND' in str(context.exception.detail)

    # ═══════════════════════════════════════════════════════════════════════════
    # Stateless Execution Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_profile__execute(self):
        """Test POST /profiles/{profile_id}/execute - stateless execution"""
        html    = self.html_gen.minimal_html()
        request = Schema__Profile__Execute__Request(html=html)
        result  = self.routes.profile__execute(profile_id='html-to-dict', request=request)

        assert type(result)           is Schema__Profile__Execute__Response
        assert str(result.profile_id) == 'html-to-dict'
        assert result.steps_total     >= 1

    def test_profile__execute__step_results(self):
        """Test that step results are populated"""
        html    = self.html_gen.minimal_html()
        request = Schema__Profile__Execute__Request(html=html)
        result  = self.routes.profile__execute(profile_id='html-to-dict', request=request)

        assert result.step_results is not None
        assert len(result.step_results) >= 1

        # Check each step result
        for step_result in result.step_results:
            assert step_result.step_type is not None

    def test_profile__execute__not_found(self):
        """Test 404 for unknown profile in execute"""
        from fastapi import HTTPException

        html    = self.html_gen.minimal_html()
        request = Schema__Profile__Execute__Request(html=html)

        with self.assertRaises(HTTPException) as context:
            self.routes.profile__execute(profile_id='unknown', request=request)

        assert context.exception.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Cached Execution Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_profile__execute__cached__not_found_cache(self):
        """Test 404 when cache_id doesn't exist"""

        request = Schema__Profile__Execute__Cached__Request()

        with self.assertRaises(HTTPException) as context:
            self.routes.profile__execute__cached(namespace   = self.namespace   ,
                                                 profile_id  = 'html-to-dict'   ,
                                                 cache_id    = Cache_Id()       ,
                                                 request     = request          )

        assert context.exception.status_code == 404
