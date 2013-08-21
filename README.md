gmond-filter-proxy
==================

Simple Python-based proxy server for a gmond server to filter out metrics that shouldn't be pushed upstream.
Heavily inspired by https://github.com/nathan-gs/ganglia-proxy-aggregator
Useful for testing, e.g. to check whether I/O performance on the gmetad machine depends on the number of metrics provided by a gmond.
