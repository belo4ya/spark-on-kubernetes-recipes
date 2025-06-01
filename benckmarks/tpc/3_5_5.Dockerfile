FROM spark:3.5.5-java17-python3

USER root

WORKDIR /opt/tpc-benchmark

RUN git clone https://github.com/NVIDIA/spark-rapids-benchmarks.git \
    && cd spark-rapids-benchmarks/nds/tpcds-gen \
    && make clean all LINUX_CC='gcc -fcommon'  \
    && cd ../../nds-h/tpch-gen  \
    && make \
