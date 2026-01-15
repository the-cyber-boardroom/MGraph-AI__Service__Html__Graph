# ═══════════════════════════════════════════════════════════════════════════════
# test_Html_LETS__Executor - Tests for LETS pipeline executor
# Tests pipeline execution, caching integration, and status tracking
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.implementations.Html_LETS__Html__To__Dict  import Html_LETS__Html__To__Dict
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.utils.Objects                                                                          import base_types
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Executor                   import Html_LETS__Executor, List__LETS__Results
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input                import Schema__LETS__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Result               import Schema__LETS__Result


class test_Html_LETS__Executor(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup
        cls.executor = Html_LETS__Executor()

    # ═══════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test auto-initialization
        with Html_LETS__Executor() as _:
            assert type(_)       is Html_LETS__Executor
            assert base_types(_) == [Type_Safe, object]
            assert _.document    is None                                         # No cache doc by default

    def test__init____with_document(self):                                       # Test with cache document
        mock_document = Type_Safe()                                              # Placeholder
        with Html_LETS__Executor(document=mock_document) as _:
            assert _.document is mock_document

    # ═══════════════════════════════════════════════════════════════════════════
    # List__LETS__Results Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_List__LETS__Results(self):                                          # Test typed results list
        results = List__LETS__Results()
        assert len(results) == 0

        result = Schema__LETS__Result(lets_name   = 'test-lets',
                                      success     = True       ,
                                      from_cache  = False      ,
                                      duration_ms = 100        )
        results.append(result)

        assert len(results)           == 1
        assert results[0].lets_name   == 'test-lets'
        assert results[0].success     is True
        assert results[0].duration_ms == 100

    def test_List__LETS__Results__multiple(self):                                # Test multiple results
        results = List__LETS__Results()

        for i in range(5):
            result = Schema__LETS__Result(lets_name   = f'lets-{i}',
                                          success     = True       ,
                                          from_cache  = i % 2 == 0 ,
                                          duration_ms = i * 10     )
            results.append(result)

        assert len(results) == 5
        assert results[0].from_cache is True
        assert results[1].from_cache is False
        assert results[4].duration_ms == 40

    # ═══════════════════════════════════════════════════════════════════════════
    # check_cache Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_check_cache__no_document(self):                                     # Test without document
        with Html_LETS__Executor() as _:
            result = _.check_cache(lets_name='html-to-dict')
            assert result is False                                               # No document = no cache

    # ═══════════════════════════════════════════════════════════════════════════
    # update_cache_status Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_update_cache_status__no_document(self):                             # Test without document
        with Html_LETS__Executor() as _:
            result = _.update_cache_status(lets_name   = 'html-to-dict',
                                           duration_ms = 100           )
            assert result is False                                               # No document = no update

    # ═══════════════════════════════════════════════════════════════════════════
    # execute_pipeline Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_execute_pipeline__empty(self):                                      # Test empty pipeline
        with Html_LETS__Executor() as _:
            context = Schema__LETS__Input()
            results = _.execute_pipeline(lets_classes = [],
                                         context      = context)
            assert len(results) == 0

    def test_execute_pipeline__single_lets(self):                                # Test single LETS
        with Html_LETS__Executor() as _:
            context = Schema__LETS__Input()
            results = _.execute_pipeline(lets_classes = [Html_LETS__Html__To__Dict],
                                         context      = context                     )
            assert len(results) == 1
            # Note: May fail due to NotImplementedError in transform - that's expected

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__executor_without_cache(self):                          # Test execution flow
        with Html_LETS__Executor() as _:
            assert _.document is None
            assert _.check_cache('any-name') is False
            assert _.update_cache_status('any-name', 50) is False
