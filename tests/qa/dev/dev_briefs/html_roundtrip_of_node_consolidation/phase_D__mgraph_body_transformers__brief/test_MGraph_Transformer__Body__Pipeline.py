from unittest                                import TestCase
from MGraph_Transformer__Body__Pipeline      import MGraph_Transformer__Body__Pipeline
from MGraph_Transformer__Body__Unwrap_Inline import MGraph_Transformer__Body__Unwrap_Inline
from MGraph_Transformer__Body__Merge_Text    import MGraph_Transformer__Body__Merge_Text

class test_MGraph_Transformer__Body__Pipeline(TestCase):        # Tests for the pipeline transformer.

    def test_pipeline__chains_transformers(self):
        pipeline = MGraph_Transformer__Body__Pipeline(
            transformers=[MGraph_Transformer__Body__Unwrap_Inline(),
                          MGraph_Transformer__Body__Merge_Text()   ]
        )

        assert pipeline.count() == 2

    def test_pipeline__fluent_api(self):
        pipeline = (MGraph_Transformer__Body__Pipeline()
            .add(MGraph_Transformer__Body__Unwrap_Inline())
            .add(MGraph_Transformer__Body__Merge_Text()))

        assert pipeline.count() == 2

    def test_pipeline__list_transformers(self):
        pipeline = (MGraph_Transformer__Body__Pipeline()
            .add(MGraph_Transformer__Body__Unwrap_Inline())
            .add(MGraph_Transformer__Body__Merge_Text()))

        names = pipeline.list_transformers()

        assert 'MGraph_Transformer__Body__Unwrap_Inline' in names
        assert 'MGraph_Transformer__Body__Merge_Text'    in names

    def test_pipeline__clear(self):
        pipeline = MGraph_Transformer__Body__Pipeline().add(MGraph_Transformer__Body__Unwrap_Inline())

        assert pipeline.count() == 1

        pipeline.clear()

        assert pipeline.count() == 0