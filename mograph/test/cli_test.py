from click.testing import CliRunner

from mograph.cli import start, stop

from .common import valid_conf

cyclic_conf = {"mysql": {"deps": ["app"]}, "app": {"deps": ["mysql"]}}


def test_start_cmd_valid():
    r = CliRunner()

    expected = (
        "START SEQUENCE\n\n"
        "0   : ['mysql', 'elasticsearch', 'zookeeper']\n"
        "1   : ['hadoop-namenode', 'kibana']\n"
        "2   : ['hbase-master']\n"
        "3   : ['fullhouse']\n"
        "4   : ['dashboard']\n"
    )

    with r.isolated_filesystem():
        with open("srv.yaml", "w") as f:
            f.write(str(valid_conf))

        result = r.invoke(start, ["srv.yaml"])

        assert result.exit_code == 0
        assert result.output == expected


def test_stop_cmd_valid():
    r = CliRunner()

    expected = (
        "STOP SEQUENCE\n\n"
        "0   : ['kibana', 'dashboard']\n"
        "1   : ['fullhouse']\n"
        "2   : ['mysql', 'hbase-master', 'elasticsearch']\n"
        "3   : ['hadoop-namenode']\n"
        "4   : ['zookeeper']\n"
    )

    with r.isolated_filesystem():
        with open("srv.yaml", "w") as f:
            f.write(str(valid_conf))

        result = r.invoke(stop, ["srv.yaml"])

        assert result.exit_code == 0
        assert result.output == expected


def test_start_cmd_invalid_yaml():
    r = CliRunner()

    with r.isolated_filesystem():
        with open("srv.yaml", "w") as f:
            f.write("This is not valid YAML: [////")

        result = r.invoke(start, ["srv.yaml"])

        assert result.exit_code == 1


def test_start_cmd_invalid_graph():
    r = CliRunner()

    with r.isolated_filesystem():
        with open("srv.yaml", "w") as f:
            f.write(str(cyclic_conf))

        result = r.invoke(start, ["srv.yaml"])

        assert result.exit_code == 1


def test_stop_cmd_invalid_graph():
    r = CliRunner()

    with r.isolated_filesystem():
        with open("srv.yaml", "w") as f:
            f.write(str(cyclic_conf))

        result = r.invoke(stop, ["srv.yaml"])

        assert result.exit_code == 1
