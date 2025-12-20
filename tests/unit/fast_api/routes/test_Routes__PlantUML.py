# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Routes__PlantUML
# ═══════════════════════════════════════════════════════════════════════════════
from unittest                                                       import TestCase
from osbot_fast_api_serverless.utils.testing.skip_tests             import skip__if_not__in_github_actions
from mgraph_ai_service_html_graph.fast_api.routes.Routes__PlantUML  import Routes__PlantUML, TAG__ROUTES_PLANTUML, ROUTES_PATHS__PLANTUML


class test_Routes__PlantUML(TestCase):

    @classmethod
    def setUpClass(cls):
        skip__if_not__in_github_actions()
        cls.routes = Routes__PlantUML()

    def test__init(self):
        assert self.routes._cache == {}
        assert self.routes.tag    == TAG__ROUTES_PLANTUML

    def test__plantuml_core_jar(self):
        response = self.routes.plantuml_core_jar()

        assert response.status_code == 200
        assert response.media_type  == 'application/java-archive'
        assert len(response.body)   > 0
        assert 'jar' in self.routes._cache

    def test__plantuml_core_jar_js(self):
        response = self.routes.plantuml_core_jar_js()

        assert response.status_code == 200
        assert response.media_type  == 'application/javascript'
        assert len(response.body)   > 0
        assert 'jar_js' in self.routes._cache

    def test__cache_hit(self):
        routes = Routes__PlantUML()                                                     # Fresh instance

        response1 = routes.plantuml_core_jar()                                          # First request - cache miss
        assert response1.headers.get('X-Proxy-Cache') == 'MISS'

        response2 = routes.plantuml_core_jar()                                          # Second request - cache hit
        assert response2.headers.get('X-Proxy-Cache') == 'HIT'

        assert response1.body == response2.body                                         # Content should match

    def test__route_paths(self):
        assert '/jars/plantuml-core.jar'    in ROUTES_PATHS__PLANTUML
        assert '/jars/plantuml-core.jar.js' in ROUTES_PATHS__PLANTUML

    def test__setup_routes(self):
        routes = Routes__PlantUML()
        result = routes.setup_routes()
        assert result is routes                                                         # Returns self for chaining