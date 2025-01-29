import pytest

from abcd_graph.callbacks.abstract import ABCDCallback


def test_must_implement_at_least_one_base_method():
    with pytest.raises(ValueError):

        class InvalidCallback(ABCDCallback): ...

    class ValidCallback(ABCDCallback):
        def before_build(self, context):
            return super().before_build(context)

    assert True

    class AnotherValidCallback(ABCDCallback):
        def after_build(self, graph, context, exporter):
            return super().after_build(graph, context, exporter)

    assert True

    class YetAnotherValidCallback(ABCDCallback):
        def before_build(self, context):
            return super().before_build(context)

        def after_build(self, graph, context, exporter):
            return super().after_build(graph, context, exporter)
