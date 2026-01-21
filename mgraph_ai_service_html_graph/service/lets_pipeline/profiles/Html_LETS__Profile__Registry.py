# ═══════════════════════════════════════════════════════════════════════════════
# Html_LETS__Profile__Registry - Registry for LETS profiles
# Manages profile registration and lookup
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id  import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict            import Type_Safe__Dict
from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.schemas.Schema__LETS__Profile         import Schema__LETS__Profile
from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.profiles.profile__html_to_dict        import PROFILE__HTML_TO_DICT
from mgraph_ai_service_html_graph.service.lets_pipeline.profiles.profiles.profile__html_to_mgraph      import PROFILE__HTML_TO_MGRAPH


# ═══════════════════════════════════════════════════════════════════════════════
# Typed Collection for Profiles
# ═══════════════════════════════════════════════════════════════════════════════

class Dict__Profiles__By_Id(Type_Safe__Dict):                                    # Profile dict by ID
    expected_key_type   = Safe_Str__Id
    expected_value_type = Schema__LETS__Profile


# ═══════════════════════════════════════════════════════════════════════════════
# Profile Registry
# ═══════════════════════════════════════════════════════════════════════════════

class Html_LETS__Profile__Registry(Type_Safe):                                   # Profile registry
    profiles : Dict__Profiles__By_Id                                             # Registered profiles

    def setup(self) -> 'Html_LETS__Profile__Registry':                           # Register built-in profiles
        self.register(PROFILE__HTML_TO_DICT)
        self.register(PROFILE__HTML_TO_MGRAPH)
        return self

    @type_safe
    def register(self, profile: Schema__LETS__Profile) -> Schema__LETS__Profile: # Register a profile
        self.profiles[profile.profile_id] = profile
        return profile

    @type_safe
    def get(self, profile_id: Safe_Str__Id) -> Schema__LETS__Profile:            # Get profile by ID
        return self.profiles.get(profile_id)

    @type_safe
    def exists(self, profile_id: Safe_Str__Id) -> bool:                          # Check if profile exists
        return profile_id in self.profiles

    def list_profiles(self) -> list:                                             # List all profile IDs
        return list(self.profiles.keys())
