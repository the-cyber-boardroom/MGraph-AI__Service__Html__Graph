# from enum                                                                       import Enum
# from typing import Any, List, Type
# from unittest                                                                   import TestCase
# from osbot_utils.testing.__                                                     import __
# from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
# from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
# from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
# from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe
#
# class Schema__LETS__Input(Type_Safe):   pass
# class Schema__LETS__Output(Type_Safe):   pass
#
# class Schema__LETS__Input__Html(Schema__LETS__Input): pass
#
# class Schema__LETS__Config(Type_Safe):
#     name        : Safe_Str__Id                    # Unique name (used in cache path)
#     description : Safe_Str__Text                  # Human readable
#
#     schema__input  : Type[Schema__LETS__Input ]  = None            # Expected input Type_Safe class
#     schema__output : Type[Schema__LETS__Output]  = None             # Output Type_Safe class
#
# class Schema__Html_Cache__Document(Type_Safe):  pass
# class Schema__LETS__Load__Input          (Type_Safe):  pass
# class Schema__LETS__Load__Output         (Type_Safe):  pass
# class Schema__LETS__Extract__Input       (Type_Safe):  pass
# class Schema__LETS__Extract__Output      (Type_Safe):  pass
# class Schema__LETS__Transform__Input     (Type_Safe):  pass
# class Schema__LETS__Transform__Output    (Type_Safe):  pass
# class Schema__LETS__Save__Input          (Type_Safe):  pass
# class Schema__LETS__Save__Output         (Type_Safe):  pass
#
# class Html_LETS__Base(Type_Safe):
#     config: Schema__LETS__Config
#
#     def load(self, load_input: Schema__LETS__Load__Input) -> Schema__LETS__Load__Output:
#         raise NotImplementedError
#
#     def extract(self, extract_input: Schema__LETS__Extract__Input) -> Schema__LETS__Extract__Output:
#         raise NotImplementedError
#
#     def transform(self, transform_input: Schema__LETS__Transform__Input) -> Schema__LETS__Transform__Output:
#         raise NotImplementedError
#
#     def save(self, save_input: Schema__LETS__Save__Input, data: Any) -> Schema__LETS__Save__Input:
#         raise NotImplementedError
#
# class Html_LETS__Html__From__Raw            (Html_LETS__Base): pass
# class Html_LETS__Html__From__Url            (Html_LETS__Base): pass
# class Html_LETS__Html__To__Dict             (Html_LETS__Base): pass
# class Html_LETS__Html__To__Html_MGraph      (Html_LETS__Base): pass
# class Html_LETS__Dict__To__Html_MGraph      (Html_LETS__Base): pass
# class Html_LETS__Html_MGraph__To__Html_Dict (Html_LETS__Base): pass
# class Html_LETS__Html_MGraph__To__Html      (Html_LETS__Base): pass
# class Html_LETS__Html_Dict__To__Html        (Html_LETS__Base): pass
#
#
#
# class Enum__Html_LETS__Type(Enum):     # Maps LETS names to their Types
#
#     HTML_FROM_RAW       = Html_LETS__Html__From__Raw
#     HTML_FROM_URL       = Html_LETS__Html__From__Url
#     HTML_TO_HTML_MGRAPH = Html_LETS__Html__To__Html_MGraph
#     HTML_MGRAPH_TO_HTML = Html_LETS__Html_MGraph__To__Html
#     # .. etc..
#
# class Schema__LETS__Profile(Type_Safe):
#     profile_id    : Safe_Str__Id
#     profile_name  : Safe_Str__Text
#     lets_pipeline : List[Type[Html_LETS__Base]]
#
# class test_Lets_storage(TestCase):
#
#     def test_Schema__LETS__Profile(self):
#
#         assert Schema__LETS__Config().obj()  == __(input_schema=None, output_schema=None, name='', description='')
#         assert Schema__LETS__Config(schema__input=Schema__LETS__Input,
#                                     schema__output=Schema__LETS__Output).obj() == __(schema__input='test_Lets_Schemas.Schema__LETS__Input',
#                                                                                      schema__output='test_Lets_Schemas.Schema__LETS__Output',
#                                                                                      name='',
#                                                                                      description='')
#
#         assert Schema__LETS__Config(schema__input=Schema__LETS__Input__Html,
#                                     schema__output=Schema__LETS__Output    ).json() == { 'description': '',
#                                                                                          'name': '',
#                                                                                          'schema__input': 'test_Lets_Schemas.Schema__LETS__Input__Html',
#                                                                                          'schema__output': 'test_Lets_Schemas.Schema__LETS__Output'}
#
#         assert Schema__LETS__Profile().obj() == __(profile_id='', profile_name='', lets_pipeline=[])
#
#         an_profile = Schema__LETS__Profile(lets_pipeline=[Html_LETS__Html__From__Raw])
#         assert an_profile.obj() == __(profile_id='', profile_name='', lets_pipeline=['test_Lets_Schemas.Html_LETS__Html__From__Raw'])
#
#         assert an_profile.json() == {'lets_pipeline': ['test_Lets_Schemas.Html_LETS__Html__From__Raw'],'profile_id': '', 'profile_name': ''}
#
#         assert Schema__LETS__Profile(lets_pipeline=[Enum__Html_LETS__Type.HTML_MGRAPH_TO_HTML.value]).obj() == __(profile_id='',
#                                                                                                                   profile_name='',
#                                                                                                                   lets_pipeline=['test_Lets_Schemas.Html_LETS__Html_MGraph__To__Html'])
#
#         another_profile = Schema__LETS__Profile(profile_id    = 'with-two-lets',
#                                                 lets_pipeline = ['test_Lets_Schemas.Html_LETS__Html__From__Raw'  ,
#                                                                   Enum__Html_LETS__Type.HTML_MGRAPH_TO_HTML.value])
#
#         another_profile_json      = another_profile.json()
#         another_profile_roundtrip = Schema__LETS__Profile.from_json(another_profile_json)
#         assert another_profile_json == {'lets_pipeline': ['test_Lets_Schemas.Html_LETS__Html__From__Raw',
#                                                            'test_Lets_Schemas.Html_LETS__Html_MGraph__To__Html'],
#                                          'profile_id': 'with-two-lets',
#                                          'profile_name': ''}
#
#         assert another_profile_roundtrip.obj() == __(profile_id='with-two-lets',
#                                                      profile_name='',
#                                                      lets_pipeline=['test_Lets_Schemas.Html_LETS__Html__From__Raw',
#                                                                     'test_Lets_Schemas.Html_LETS__Html_MGraph__To__Html'])
#
#         assert another_profile_roundtrip.obj() == another_profile.obj()
#         assert another_profile_roundtrip.json() == another_profile.json()
#
#         @type_safe
#         def convert_to_lets(lets_type: Enum__Html_LETS__Type) -> Type[Html_LETS__Base]:
#             return lets_type.value
#
#         assert convert_to_lets(Enum__Html_LETS__Type.HTML_MGRAPH_TO_HTML) == Html_LETS__Html_MGraph__To__Html
#         assert convert_to_lets('HTML_MGRAPH_TO_HTML'                    ) == Html_LETS__Html_MGraph__To__Html
#
#
#
#
#
#
#
