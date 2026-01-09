# ═══════════════════════════════════════════════════════════════════════════════
# MGraph_Transformer__Body__Pipeline - Chain multiple body transformers
# Part of Phase D: MGraph Body Transformers
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                         import List
from mgraph_db.mgraph.MGraph                        import MGraph
from MGraph_Transformer__Body__Base                 import MGraph_Transformer__Body__Base


class MGraph_Transformer__Body__Pipeline(MGraph_Transformer__Body__Base):
    """Chain multiple body transformers to apply in sequence.

    Usage:
        pipeline = MGraph_Transformer__Body__Pipeline(
            transformers = [ MGraph_Transformer__Body__Unwrap_Inline(),
                             MGraph_Transformer__Body__Merge_Text()   ]
        )
        pipeline.transform(body_graph)

        # Or with fluent API:
        pipeline = (MGraph_Transformer__Body__Pipeline()
            .add(MGraph_Transformer__Body__Unwrap_Inline())
            .add(MGraph_Transformer__Body__Merge_Text()))
        pipeline.transform(body_graph)
    """

    transformers: list = None                                                   # List of transformers to apply

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.transformers is None:
            self.transformers = []

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Transform
    # ═══════════════════════════════════════════════════════════════════════════

    def transform(self, mgraph: MGraph) -> MGraph:
        """Apply all transformers in sequence."""
        for transformer in self.transformers:
            transformer.transform(mgraph)
        return mgraph

    # ═══════════════════════════════════════════════════════════════════════════
    # Fluent API
    # ═══════════════════════════════════════════════════════════════════════════

    def add(self, transformer: MGraph_Transformer__Body__Base) -> 'MGraph_Transformer__Body__Pipeline':
        """Add a transformer to the pipeline. Returns self for chaining."""
        self.transformers.append(transformer)
        return self

    def clear(self) -> 'MGraph_Transformer__Body__Pipeline':
        """Remove all transformers from the pipeline. Returns self for chaining."""
        self.transformers = []
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Introspection
    # ═══════════════════════════════════════════════════════════════════════════

    def count(self) -> int:
        """Return number of transformers in pipeline."""
        return len(self.transformers)

    def list_transformers(self) -> List[str]:
        """Return list of transformer class names."""
        return [type(t).__name__ for t in self.transformers]