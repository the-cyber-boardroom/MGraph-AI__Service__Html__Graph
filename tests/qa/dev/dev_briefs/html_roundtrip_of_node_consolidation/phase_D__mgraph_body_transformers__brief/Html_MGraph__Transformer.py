# ═══════════════════════════════════════════════════════════════════════════════
# Html_MGraph__Transformer - Helper class for HTML → Transform → HTML workflow
# Part of Phase D: MGraph Body Transformers
#
# Provides a simple API for transforming HTML through MGraph transformers
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                      import List, Type
from osbot_utils.type_safe.Type_Safe             import Type_Safe
from MGraph_Transformer__Body__Base              import MGraph_Transformer__Body__Base
from MGraph_Transformer__Body__Pipeline          import MGraph_Transformer__Body__Pipeline
from MGraph_Transformer__Body__Remove_By_Tag     import MGraph_Transformer__Body__Remove_By_Tag
from MGraph_Transformer__Body__Unwrap_Inline     import MGraph_Transformer__Body__Unwrap_Inline
from MGraph_Transformer__Body__Merge_Text        import MGraph_Transformer__Body__Merge_Text
from MGraph_Transformer__Body__Remove_Empty_Text import MGraph_Transformer__Body__Remove_Empty_Text


class Html_MGraph__Transformer(Type_Safe):
    """Helper class for HTML transformation via MGraph.

    Provides a simple API for the common workflow:
        HTML → MGraph → Transform → HTML

    Usage:
        # Simple usage with default transformers
        transformer = Html_MGraph__Transformer()
        clean_html = transformer.transform(html)

        # Custom pipeline
        transformer = Html_MGraph__Transformer(
            transformers=[
                MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove={'script'}),
                MGraph_Transformer__Body__Unwrap_Inline(),
            ]
        )
        clean_html = transformer.transform(html)

        # Fluent API
        clean_html = (Html_MGraph__Transformer()
            .add(MGraph_Transformer__Body__Unwrap_Inline())
            .add(MGraph_Transformer__Body__Merge_Text())
            .transform(html))
    """

    transformers: list = None                                                   # List of transformers to apply
    pipeline    : MGraph_Transformer__Body__Pipeline = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.transformers is None:
            self.transformers = []
        self.pipeline = MGraph_Transformer__Body__Pipeline(transformers=self.transformers)

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Transform Method
    # ═══════════════════════════════════════════════════════════════════════════

    def transform(self, html: str) -> str:
        """Transform HTML through the pipeline.

        Args:
            html: Input HTML string

        Returns:
            Transformed HTML string
        """
        doc        = self.html_to_mgraph_document(html)                         # HTML → MGraph
        body_graph = doc.body_graph.mgraph

        self.pipeline.transform(body_graph)                                     # Transform

        return self.mgraph_document_to_html(doc)                                # MGraph → HTML

    # ═══════════════════════════════════════════════════════════════════════════
    # Fluent API
    # ═══════════════════════════════════════════════════════════════════════════

    def add(self, transformer: MGraph_Transformer__Body__Base) -> 'Html_MGraph__Transformer':
        """Add a transformer to the pipeline. Returns self for chaining."""
        self.pipeline.add(transformer)
        return self

    def clear(self) -> 'Html_MGraph__Transformer':
        """Clear all transformers. Returns self for chaining."""
        self.pipeline.clear()
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Conversion Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def html_to_mgraph_document(self, html: str):
        """Convert HTML to Html_MGraph__Document using Phase A + B."""
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_Dict__With__Node_Ids            import Html__To__Html_Dict__With__Node_Ids
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html__To__Html_MGraph__Document__Node_Id_Reuse import Html__To__Html_MGraph__Document__Node_Id_Reuse

        html_dict = Html__To__Html_Dict__With__Node_Ids(html=html).convert()
        doc       = Html__To__Html_MGraph__Document__Node_Id_Reuse().convert_from_dict(html_dict)
        return doc

    def mgraph_document_to_html(self, doc) -> str:
        """Convert Html_MGraph__Document back to HTML."""
        from mgraph_ai_service_html_graph.service.html_mgraph.converters.Html_MGraph__Document__To__Html import Html_MGraph__Document__To__Html

        return Html_MGraph__Document__To__Html().convert(doc)

    # ═══════════════════════════════════════════════════════════════════════════
    # Introspection
    # ═══════════════════════════════════════════════════════════════════════════

    def count(self) -> int:
        """Return number of transformers in pipeline."""
        return self.pipeline.count()

    def list_transformers(self) -> List[str]:
        """Return list of transformer class names."""
        return self.pipeline.list_transformers()


# ═══════════════════════════════════════════════════════════════════════════════
# Factory Functions for Common Pipelines
# ═══════════════════════════════════════════════════════════════════════════════

def create_flatten_transformer() -> Html_MGraph__Transformer:
    """Create transformer that flattens inline elements.

    Removes: <a>, <b>, <i>, <span>, <strong>, <em>, etc.
    Merges: Adjacent text nodes
    Removes: Empty/whitespace text nodes
    """

    return Html_MGraph__Transformer(
        transformers=[MGraph_Transformer__Body__Unwrap_Inline()    ,
                      MGraph_Transformer__Body__Merge_Text()       ,
                      MGraph_Transformer__Body__Remove_Empty_Text()]
    )


def create_clean_transformer(remove_tags: set = None) -> Html_MGraph__Transformer:
    """Create transformer that cleans HTML for text extraction.

    Args:
        remove_tags: Tags to remove entirely (default: script, style, nav, footer, header)

    Removes: Specified tags and their content
    Removes: Inline wrappers (keeps text)
    Merges: Adjacent text nodes
    Removes: Empty/whitespace text nodes
    """

    if remove_tags is None:
        remove_tags = {'script', 'style', 'nav', 'footer', 'header', 'aside'}

    return Html_MGraph__Transformer(
        transformers=[MGraph_Transformer__Body__Remove_By_Tag(tags_to_remove=remove_tags),
                      MGraph_Transformer__Body__Unwrap_Inline()                          ,
                      MGraph_Transformer__Body__Merge_Text()                             ,
                      MGraph_Transformer__Body__Remove_Empty_Text()                      ]
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience Function
# ═══════════════════════════════════════════════════════════════════════════════

def transform_html(html: str, transformers: list = None) -> str:
    """One-liner HTML transformation.

    Args:
        html: Input HTML string
        transformers: List of transformers (default: flatten pipeline)

    Returns:
        Transformed HTML string

    Usage:
        # Default flatten
        clean = transform_html('<div>Hello <b>World</b>!</div>')

        # Custom transformers
        clean = transform_html(html, transformers=[
            MGraph_Transformer__Body__Unwrap_Inline()
        ])
    """
    if transformers is None:
        return create_flatten_transformer().transform(html)

    return Html_MGraph__Transformer(transformers=transformers).transform(html)