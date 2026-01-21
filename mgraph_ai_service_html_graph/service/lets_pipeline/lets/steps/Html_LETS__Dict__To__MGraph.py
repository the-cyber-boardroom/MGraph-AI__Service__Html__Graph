# ═══════════════════════════════════════════════════════════════════════════════
# Html_LETS__Dict__To__MGraph - LETS for converting HTML Dict to MGraph
# Builds MGraph document from parsed HTML dictionary
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                                         import Dict, Any
from osbot_utils.type_safe.Type_Safe                                                                                import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                      import type_safe
from osbot_utils.helpers.flows.decorators.task                                                                      import task
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base                                   import Html_LETS__Base
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config                           import Schema__LETS__Config
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Input            import Schema__LETS__Load__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_load.Schema__LETS__Load__Output           import Schema__LETS__Load__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_extract.Schema__LETS__Extract__Output     import Schema__LETS__Extract__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_transform.Schema__LETS__Transform__Output import Schema__LETS__Transform__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.lets_save.Schema__LETS__Save__Output           import Schema__LETS__Save__Output
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.safe_str.Safe_Str__LETS__Name                  import Safe_Str__LETS__Name
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.steps.Html_LETS__Html__To__Dict                        import Schema__Html_Dict


# ═══════════════════════════════════════════════════════════════════════════════
# MGraph Document Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__MGraph_Document(Type_Safe):
    mgraph_data : Dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# Extended Schemas for Dict→MGraph Pipeline
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Dict_To_MGraph__Load__Input(Schema__LETS__Load__Input):
    html_dict : Schema__Html_Dict = None


class Schema__Dict_To_MGraph__Load__Output(Schema__LETS__Load__Output):
    html_dict : Schema__Html_Dict = None


class Schema__Dict_To_MGraph__Extract__Output(Schema__LETS__Extract__Output):
    html_dict : Schema__Html_Dict = None


class Schema__Dict_To_MGraph__Transform__Output(Schema__LETS__Transform__Output):
    mgraph_document : Schema__MGraph_Document = None


# ═══════════════════════════════════════════════════════════════════════════════
# Action Functions
# ═══════════════════════════════════════════════════════════════════════════════

@task()
@type_safe
def action__dict_to_mgraph__load(self,
                                 input_data: Schema__Dict_To_MGraph__Load__Input
                            ) -> Schema__Dict_To_MGraph__Load__Output:
    return Schema__Dict_To_MGraph__Load__Output(html_dict=input_data.html_dict)


@task()
@type_safe
def action__dict_to_mgraph__extract(self,
                                    input_data: Schema__Dict_To_MGraph__Load__Output
                               ) -> Schema__Dict_To_MGraph__Extract__Output:
    return Schema__Dict_To_MGraph__Extract__Output(html_dict=input_data.html_dict)


@task()
@type_safe
def action__dict_to_mgraph__transform(self,
                                      input_data: Schema__Dict_To_MGraph__Extract__Output
                                 ) -> Schema__Dict_To_MGraph__Transform__Output:
    html_dict   = input_data.html_dict
    mgraph_data = build_mgraph(html_dict)
    return Schema__Dict_To_MGraph__Transform__Output(mgraph_document=Schema__MGraph_Document(mgraph_data=mgraph_data))


@task()
@type_safe
def action__dict_to_mgraph__save(self,
                                 input_data: Schema__Dict_To_MGraph__Transform__Output
                            ) -> Schema__LETS__Save__Output:
    return Schema__LETS__Save__Output(success=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

def build_mgraph(html_dict: Schema__Html_Dict) -> Dict[str, Any]:
    if html_dict is None:
        return {'graph': {'nodes': [], 'edges': []}, 'source': {}}
    return {'graph' : {'nodes': [], 'edges': []}  ,
            'source': html_dict.html_dict         }


# ═══════════════════════════════════════════════════════════════════════════════
# LETS Implementation
# ═══════════════════════════════════════════════════════════════════════════════

class Html_LETS__Dict__To__MGraph(Html_LETS__Base):

    load      = action__dict_to_mgraph__load
    extract   = action__dict_to_mgraph__extract
    transform = action__dict_to_mgraph__transform
    save      = action__dict_to_mgraph__save

    def setup(self) -> 'Html_LETS__Dict__To__MGraph':
        self.config = Schema__LETS__Config(name        = Safe_Str__LETS__Name('dict-to-mgraph')      ,
                                           description = 'Build MGraph document from HTML dictionary')
        return self