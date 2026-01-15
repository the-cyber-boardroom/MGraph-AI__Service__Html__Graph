# ═══════════════════════════════════════════════════════════════════════════════
# Html_LETS__Executor - Executes LETS transformations and pipelines
# Manages caching, status tracking, and pipeline orchestration
# ═══════════════════════════════════════════════════════════════════════════════

import time
from typing                                                                                            import Type, List
from osbot_utils.type_safe.Type_Safe                                                                   import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                         import type_safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                   import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                        import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                                  import Type_Safe__List
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base                      import Html_LETS__Base
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Input               import Schema__LETS__Input
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Result              import Schema__LETS__Result
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Status              import Schema__LETS__Status
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.safe_str.Safe_Str__LETS__Name             import Safe_Str__LETS__Name
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.safe_str.Safe_Str__LETS__Data_Key         import Safe_Str__LETS__Data_Key


# ═══════════════════════════════════════════════════════════════════════════════
# Typed Collection for Results
# ═══════════════════════════════════════════════════════════════════════════════

class List__LETS__Results(Type_Safe__List):                                      # List of LETS results
    expected_type = Schema__LETS__Result


# ═══════════════════════════════════════════════════════════════════════════════
# LETS Executor
# ═══════════════════════════════════════════════════════════════════════════════

class Html_LETS__Executor(Type_Safe):                                            # Pipeline executor
    document : Type_Safe = None                                                  # Optional Html_Cache__Document

    # ═══════════════════════════════════════════════════════════════════════════
    # Single LETS Execution
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def execute_single(self                               ,                      # Execute one LETS
                       lets_class : Type[Html_LETS__Base] ,                      # LETS class to execute
                       context    : Schema__LETS__Input   ,                      # Input context
                       force      : bool = False                                 # Force rebuild
                  ) -> Schema__LETS__Result:
        start_time    = time.time()
        lets_instance = lets_class()
        lets_instance.setup()
        lets_name     = lets_instance.config.name

        # Check cache if document available and not forcing
        if self.document and force is False:
            cached = self.check_cache(lets_name = lets_name)
            if cached:
                duration_ms = Safe_UInt(int((time.time() - start_time) * 1000))
                return Schema__LETS__Result(lets_name   = lets_name   ,
                                            success     = True        ,
                                            from_cache  = True        ,
                                            duration_ms = duration_ms )

        # Execute LETS phases
        try:
            load_output      = lets_instance.load(context)
            extract_output   = lets_instance.extract(load_output)
            transform_output = lets_instance.transform(extract_output)
            save_output      = lets_instance.save(transform_output)
            success          = save_output.success
        except Exception as e:
            duration_ms = Safe_UInt(int((time.time() - start_time) * 1000))
            return Schema__LETS__Result(lets_name   = lets_name       ,
                                        success     = False           ,
                                        from_cache  = False           ,
                                        duration_ms = duration_ms     ,
                                        error       = str(e)          )

        # Calculate duration
        duration_ms = Safe_UInt(int((time.time() - start_time) * 1000))

        # Update cache status if document available
        if self.document and success:
            self.update_cache_status(lets_name   = lets_name  ,
                                     duration_ms = duration_ms)

        return Schema__LETS__Result(lets_name   = lets_name  ,
                                    success     = success    ,
                                    from_cache  = False      ,
                                    duration_ms = duration_ms)

    # ═══════════════════════════════════════════════════════════════════════════
    # Pipeline Execution
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def execute_pipeline(self                                     ,              # Execute LETS pipeline
                         lets_classes : List[Type[Html_LETS__Base]],             # Ordered LETS classes
                         context      : Schema__LETS__Input       ,              # Initial input
                         force_layers : List[Safe_Str__LETS__Name] = None        # Layers to force
                    ) -> List__LETS__Results:
        results       = List__LETS__Results()
        force_layers  = force_layers or []
        current_context = context

        for lets_class in lets_classes:
            lets_instance = lets_class()
            lets_instance.setup()
            lets_name     = lets_instance.config.name
            force         = lets_name in force_layers

            result = self.execute_single(lets_class = lets_class     ,
                                         context    = current_context,
                                         force      = force          )
            results.append(result)

            if result.success is False:
                break                                                            # Stop pipeline on failure

        return results

    # ═══════════════════════════════════════════════════════════════════════════
    # Profile Execution
    # ═══════════════════════════════════════════════════════════════════════════

    @type_safe
    def execute_profile(self                             ,                       # Execute LETS profile
                        profile : Type_Safe              ,                       # Schema__LETS__Profile
                        context : Schema__LETS__Input    ,                       # Initial input
                        force_layers : List[Safe_Str__LETS__Name] = None         # Layers to force
                   ) -> List__LETS__Results:
        return self.execute_pipeline(lets_classes = profile.lets_pipeline,
                                     context      = context              ,
                                     force_layers = force_layers         )

    # ═══════════════════════════════════════════════════════════════════════════
    # Cache Integration (called when self.document is set)
    # ═══════════════════════════════════════════════════════════════════════════

    def check_cache(self, lets_name: Safe_Str__LETS__Name) -> bool:              # Check if cached
        if self.document is None:
            return False
        status = self.document.get_lets_status(name = lets_name)
        if status and status.completed:
            return True
        return False

    def update_cache_status(self                               ,                 # Update cache status
                            lets_name   : Safe_Str__LETS__Name ,
                            duration_ms : Safe_UInt
                       ) -> bool:
        if self.document is None:
            return False
        status = Schema__LETS__Status(name        = lets_name                      ,
                                      completed   = True                           ,
                                      data_key    = Safe_Str__LETS__Data_Key(lets_name),
                                      file_id     = Safe_Str__Id(lets_name)        ,
                                      duration_ms = duration_ms                    )
        return self.document.update_lets_status(status = status)
