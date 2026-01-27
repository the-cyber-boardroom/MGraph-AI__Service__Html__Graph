import mgraph_ai_service_html_graph__render_ui
from fastapi                                                                                import Response
from osbot_fast_api.api.routes.Fast_API__Routes                                             import Fast_API__Routes
from mgraph_ai_service_html_graph.service.ifd_snapshot.IFD_Snapshot                         import IFD_Snapshot
from mgraph_ai_service_html_graph.service.ifd_snapshot.schemas.Schema__IFD_Snapshot_Config  import Schema__IFD_Snapshot_Config

TAG__ROUTES_IFD_SNAPSHOT = 'ifd/snapshot'

ROUTES_PATHS__IFD_SNAPSHOT = [
    f'/{TAG__ROUTES_IFD_SNAPSHOT}' + '/create',
]


class Routes__IFD__Snapshot(Fast_API__Routes):                                 # Routes for cache document operations
    tag          : str               = TAG__ROUTES_IFD_SNAPSHOT


    def create(self):
        base_path      = '/v0/v0.2'
        #target_version = 'v0.2.10'
        target_version = 'v0.2.11'
        fixtures_path  = mgraph_ai_service_html_graph__render_ui.path + base_path
        config = Schema__IFD_Snapshot_Config(version_root   = fixtures_path,
                                             target_version = target_version)

        with IFD_Snapshot(config=config) as _:
            result  = _.generate()
            content = result.content_text
            return Response(content=content, media_type="text/plain")

    def setup_routes(self):
        self.add_route_get(self.create)