# ═══════════════════════════════════════════════════════════════════════════════
# Html_LETS__Html__From__Raw - LETS step for receiving raw HTML input
# First step in most pipelines - receives and stores raw HTML
#
#    LETS step for receiving raw HTML input.
#
#    This is typically the first step in a pipeline. It receives raw HTML,
#    computes basic statistics, and stores it in the cache.
#
#    Pipeline:
#    - Load: Passthrough (HTML provided directly as input)
#    - Extract: Passthrough (no extraction needed)
#    - Transform: Compute statistics (char_count, tag_count, line_count)
#    - Save: Store in cache layer 'raw-html' with file_id 'source'
#
#    Usage:
#        step = Html_LETS__Html__From__Raw(document=doc).setup()
#        result = step.execute(Schema__LETS__Load__Input(html='<html>...'))
#
#        # Observability
#        print(step.durations())      # Timing per action
#        print(step.captured_logs())  # Log messages
#
# ═══════════════════════════════════════════════════════════════════════════════
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.actions.extract.lets__action__extract__passthrough         import lets__action__extract__passthrough
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.actions.load.lets__action__load__passthrough               import lets__action__load__passthrough
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.actions.save.lets__action__save__to__cache_service         import lets__action__save__to__cache_service
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.actions.transform.lets__action__transform__compute_stats   import lets__action__transform__compute_stats
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.base.Html_LETS__Base                                       import Html_LETS__Base
from mgraph_ai_service_html_graph.service.lets_pipeline.lets.schemas.Schema__LETS__Config                               import Schema__LETS__Config


class Html_LETS__Html__From__Raw(Html_LETS__Base):                  # Declarative action wiring - each L-E-T-S phase uses a reusable action

    load      = lets__action__load__passthrough
    extract   = lets__action__extract__passthrough
    transform = lets__action__transform__compute_stats
    save      = lets__action__save__to__cache_service
    
    def setup(self) -> 'Html_LETS__Html__From__Raw':        # Initialize step configuration.
        self.config = (
            Schema__LETS__Config(name          = 'html-from-raw'   ,
                                 description   = 'Load raw HTML and store in cache'     ,
                                 save_layer    = 'raw-html'                             ,
                                 save_file_id  = 'source'                               ,
                                 save_type     = 'string'                               ,
                                 compute_stats = True                                   ))
        return self
