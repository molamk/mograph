import pytest

from mograph.exceptions import CyclicGraphError, UndefinedProviderError
from mograph.graph import config_to_graph

from .common import valid_conf


class TestGraph:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    # Valid graphs
    def test_graph_gen_basic(self):
        conf = {"mysql": {}, "app": {"deps": ["mysql"]}}

        g = config_to_graph(conf)
        g.validate()

        assert g.size() == 2
        assert g.has_consumer("mysql")
        assert g.has_consumer("app")
        assert g.has_edge("app", "mysql")

    def test_graph_gen_with_pending(self):
        conf = {"app": {"deps": ["mysql"]}, "mysql": {}}

        g = config_to_graph(conf)
        g.validate()

        assert g.size() == 2
        assert g.has_consumer("mysql")
        assert g.has_consumer("app")
        assert g.has_edge("app", "mysql")

    # Invalid graphs
    def test_graph_with_missing_dependency(self):
        conf = {"mysql": {}, "app": {"deps": ["mongodb"]}}

        g = config_to_graph(conf)

        with pytest.raises(UndefinedProviderError) as e:
            g.validate()

        assert e.value.consumers == ["app"]
        assert e.value.provider == "mongodb"

    def test_graph_with_cycle(self):
        conf = {"mysql": {"deps": ["app"]}, "app": {"deps": ["mysql"]}}

        g = config_to_graph(conf)

        with pytest.raises(CyclicGraphError) as e:
            g.validate()

        assert e.value.origin == "app"
        assert e.value.destination == "mysql"

    # Start & Stop sequences
    def test_start_stop_sequences_basic(self):
        conf = {
            "mysql": {},
            "zookeeper": {},
            "kibana": {"deps": ["mysql"]},
            "fullhouse": {"deps": ["kibana", "zookeeper"]},
        }

        g = config_to_graph(conf)
        g.validate()

        print(g)

        # Start sequence
        start_seq = [["mysql", "zookeeper"], ["kibana"], ["fullhouse"]]

        assert g.get_all_levels() == start_seq

        # Stop sequence
        stop_seq = [["fullhouse"], ["zookeeper", "kibana"], ["mysql"]]

        g.reverse_dependencies()
        assert g.get_all_levels() == stop_seq

    def test_start_stop_sequences_main(self):
        print(valid_conf)
        g = config_to_graph(valid_conf)
        g.validate()

        # Start sequence
        start_seq = [
            ["mysql", "elasticsearch", "zookeeper"],
            ["hadoop-namenode", "kibana"],
            ["hbase-master"],
            ["fullhouse"],
            ["dashboard"],
        ]

        assert g.get_all_levels() == start_seq

        # Stop sequence
        stop_seq = [
            ["kibana", "dashboard"],
            ["fullhouse"],
            ["mysql", "hbase-master", "elasticsearch"],
            ["hadoop-namenode"],
            ["zookeeper"],
        ]

        g.reverse_dependencies()
        assert g.get_all_levels() == stop_seq

    # Representations
    def test_str(self):
        conf = {"mysql": {}, "app": {"deps": ["mysql"]}}

        expected = "mysql               : []\n" "app                 : ['mysql']"

        g = config_to_graph(conf)

        assert g.__str__() == expected

    def test_repr(self):
        conf = {"mysql": {}, "app": {"deps": ["mysql"]}}

        expected = [[], [0]]

        g = config_to_graph(conf)

        assert g.__repr__() == repr(expected)
