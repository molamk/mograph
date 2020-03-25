valid_conf = {
    "mysql": {"hosts": ["hostname-rm"]},
    "hadoop-namenode": {"deps": ["zookeeper"], "hosts": ["hostname-rm"]},
    "hbase-master": {"deps": ["hadoop-namenode"], "hosts": ["hostname-rm"]},
    "fullhouse": {
        "deps": ["mysql", "elasticsearch", "hbase-master"],
        "hosts": ["hostname-01", "hostname-02", "hostname-03"],
    },
    "kibana": {"deps": ["mysql"], "hosts": ["hostname-rm"]},
    "dashboard": {"deps": ["fullhouse"], "hosts": ["hostname-rm"]},
    "elasticsearch": {"hosts": ["hostname-01", "hostname-02", "hostname-03"]},
    "zookeeper": {"hosts": ["hostname-01", "hostname-02", "hostname-03"]},
}
