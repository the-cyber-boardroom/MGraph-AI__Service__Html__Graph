# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_LETS__Profile__Registry - Tests for profile registry
# Tests profile registration, lookup, and built-in profiles
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.utils.Objects                                                                      import base_types
from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.Html_LETS__Profile__Registry       import Html_LETS__Profile__Registry
from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.Html_LETS__Profile__Registry       import Dict__Profiles__By_Id
from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.schemas.Schema__LETS__Profile      import Schema__LETS__Profile
from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.profiles.profile__html_to_dict     import PROFILE__HTML_TO_DICT
from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.profiles.profile__html_to_mgraph   import PROFILE__HTML_TO_MGRAPH
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Html__To__Dict        import Html_LETS__Html__To__Dict
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Dict__To__MGraph      import Html_LETS__Dict__To__MGraph


class test_Html_LETS__Profile__Registry(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with Html_LETS__Profile__Registry() as _:
            assert type(_)        is Html_LETS__Profile__Registry
            assert base_types(_)  == [Type_Safe, object]
            assert type(_.profiles) is Dict__Profiles__By_Id

    def test__init____profiles_empty(self):                                      # Test profiles start empty
        with Html_LETS__Profile__Registry() as _:
            assert len(_.profiles) == 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_setup(self):                                                        # Test setup registers built-ins
        with Html_LETS__Profile__Registry() as _:
            result = _.setup()

            assert result             is _                                       # Returns self
            assert len(_.profiles)    >= 2                                       # At least 2 built-in profiles
            assert _.exists('html-to-dict')   is True
            assert _.exists('html-to-mgraph') is True

    def test_setup__returns_self(self):                                          # Test chaining
        registry = Html_LETS__Profile__Registry().setup()
        assert type(registry) is Html_LETS__Profile__Registry

    # ═══════════════════════════════════════════════════════════════════════════
    # Register Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_register(self):                                                     # Test registers profile
        with Html_LETS__Profile__Registry() as _:
            profile = Schema__LETS__Profile(profile_id    = 'custom-profile'  ,
                                            profile_name  = 'Custom Profile'  ,
                                            description   = 'Test profile'    ,
                                            lets_pipeline = [Html_LETS__Html__To__Dict])

            result = _.register(profile=profile)

            assert result is profile
            assert _.exists('custom-profile') is True

    def test_register__overwrites(self):                                         # Test overwrites existing
        with Html_LETS__Profile__Registry() as _:
            profile1 = Schema__LETS__Profile(profile_id   = 'same-id'        ,
                                             profile_name = 'First Profile'  ,
                                             lets_pipeline = [])
            profile2 = Schema__LETS__Profile(profile_id   = 'same-id'        ,
                                             profile_name = 'Second Profile' ,
                                             lets_pipeline = [])

            _.register(profile=profile1)
            _.register(profile=profile2)

            retrieved = _.get('same-id')
            assert retrieved.profile_name == 'Second Profile'

    # ═══════════════════════════════════════════════════════════════════════════
    # Get Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get(self):                                                          # Test gets profile
        with Html_LETS__Profile__Registry().setup() as _:
            profile = _.get('html-to-dict')

            assert profile                is not None
            assert profile.profile_id     == 'html-to-dict'
            assert profile.profile_name   == 'HTML to Dictionary'

    def test_get__html_to_mgraph(self):                                          # Test gets mgraph profile
        with Html_LETS__Profile__Registry().setup() as _:
            profile = _.get('html-to-mgraph')

            assert profile              is not None
            assert profile.profile_id   == 'html-to-mgraph'
            assert len(profile.lets_pipeline) == 2

    def test_get__not_found(self):                                               # Test returns None
        with Html_LETS__Profile__Registry().setup() as _:
            profile = _.get('nonexistent')

            assert profile is None

    # ═══════════════════════════════════════════════════════════════════════════
    # Exists Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_exists__true(self):                                                 # Test returns True
        with Html_LETS__Profile__Registry().setup() as _:
            assert _.exists('html-to-dict')   is True
            assert _.exists('html-to-mgraph') is True

    def test_exists__false(self):                                                # Test returns False
        with Html_LETS__Profile__Registry().setup() as _:
            assert _.exists('nonexistent') is False
            assert _.exists('')            is False

    # ═══════════════════════════════════════════════════════════════════════════
    # list_profiles Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_list_profiles(self):                                                # Test lists all profiles
        with Html_LETS__Profile__Registry().setup() as _:
            profiles = _.list_profiles()

            assert type(profiles)      is list
            assert len(profiles)       >= 2
            assert 'html-to-dict'      in [str(p) for p in profiles]
            assert 'html-to-mgraph'    in [str(p) for p in profiles]

    def test_list_profiles__empty(self):                                         # Test empty list
        with Html_LETS__Profile__Registry() as _:
            profiles = _.list_profiles()

            assert profiles == []

    # ═══════════════════════════════════════════════════════════════════════════
    # Built-in Profile Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_builtin__PROFILE__HTML_TO_DICT(self):                               # Test html-to-dict profile
        assert PROFILE__HTML_TO_DICT.profile_id     == 'html-to-dict'
        assert PROFILE__HTML_TO_DICT.profile_name   == 'HTML to Dictionary'
        assert len(PROFILE__HTML_TO_DICT.lets_pipeline) == 1
        assert PROFILE__HTML_TO_DICT.lets_pipeline[0] is Html_LETS__Html__To__Dict

    def test_builtin__PROFILE__HTML_TO_MGRAPH(self):                             # Test html-to-mgraph profile
        assert PROFILE__HTML_TO_MGRAPH.profile_id   == 'html-to-mgraph'
        assert PROFILE__HTML_TO_MGRAPH.profile_name == 'HTML to MGraph'
        assert len(PROFILE__HTML_TO_MGRAPH.lets_pipeline) == 2
        assert PROFILE__HTML_TO_MGRAPH.lets_pipeline[0] is Html_LETS__Html__To__Dict
        assert PROFILE__HTML_TO_MGRAPH.lets_pipeline[1] is Html_LETS__Dict__To__MGraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Dict__Profiles__By_Id Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_Dict__Profiles__By_Id(self):                                        # Test typed dict
        profiles_dict = Dict__Profiles__By_Id()

        assert len(profiles_dict) == 0

        profile = Schema__LETS__Profile(profile_id   = 'test'          ,
                                        profile_name = 'Test'          ,
                                        lets_pipeline = [])
        profiles_dict['test'] = profile

        assert len(profiles_dict)        == 1
        assert profiles_dict['test']     is profile

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__register_and_use(self):                                # Test full registration flow
        with Html_LETS__Profile__Registry().setup() as _:
            # Create custom profile
            custom = Schema__LETS__Profile(profile_id    = 'custom-full'               ,
                                           profile_name  = 'Custom Full Pipeline'      ,
                                           description   = 'Custom HTML to MGraph'     ,
                                           lets_pipeline = [Html_LETS__Html__To__Dict ,
                                                            Html_LETS__Dict__To__MGraph])

            # Register
            _.register(profile=custom)

            # Verify registered
            assert _.exists('custom-full') is True

            # Retrieve
            retrieved = _.get('custom-full')
            assert retrieved.profile_name == 'Custom Full Pipeline'
            assert len(retrieved.lets_pipeline) == 2

            # List should include new profile
            all_profiles = _.list_profiles()
            assert 'custom-full' in [str(p) for p in all_profiles]

    def test_integration__instantiate_pipeline(self):                            # Test using profile pipeline
        with Html_LETS__Profile__Registry().setup() as _:
            profile = _.get('html-to-mgraph')

            # Instantiate all LETS in pipeline
            instances = []
            for lets_class in profile.lets_pipeline:
                instance = lets_class().setup()
                instances.append(instance)

            # Verify instances
            assert len(instances)            == 2
            assert instances[0].config.name  == 'html-to-dict'
            assert instances[1].config.name  == 'dict-to-mgraph'
