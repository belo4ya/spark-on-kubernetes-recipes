FROM spark:3.5.5-java17-python3

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    bison \
    flex \
    byacc \
    dos2unix \
    maven \
    unzip \
    wget \
    awscli \
    git \
    nano \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -P $SPARK_HOME/jars \
    && wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.783/aws-java-sdk-bundle-1.12.783.jar -P $SPARK_HOME/jars \
    && wget https://repo1.maven.org/maven2/org/apache/spark/spark-hadoop-cloud_2.13/3.5.5/spark-hadoop-cloud_2.13-3.5.5.jar -P $SPARK_HOME/jars
#wget https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.31.43/bundle-2.31.43.jar
#wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.4.1/hadoop-aws-3.4.1.jar

WORKDIR /opt/tpc-benchmark

ARG AWS_ACCESS_KEY_ID=90944e28e308450a98dbecc9eae1c0ef
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_ENDPOINT_URL=https://s3.ru-7.storage.selcloud.ru
ARG S3_BUCKET=spark-benchmark

ENV AWS_ENDPOINT_URL=${AWS_ENDPOINT_URL}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV S3_BUCKET=${S3_BUCKET}

# TPC-H
RUN aws --endpoint-url=${AWS_ENDPOINT_URL} --no-verify-ssl s3 cp s3://${S3_BUCKET}/tpc-h/tpc-h-tool-v3.0.1.zip . \
    && unzip tpc-h-tool-v3.0.1.zip \
    && rm -f tpc-h-tool-v3.0.1.zip \
    && cd tpc-h-tool-v3.0.1/dbgen \
    && make -f makefile.suite CC=gcc MACHINE=LINUX WORKLOAD=TPCH DATABASE=ORACLE \
    && chmod +x dbgen qgen \
    && cp qgen dbgen /usr/local/bin/

ENV TPCH_HOME=/opt/tpc-benchmark/tpc-h-tool-v3.0.1
ENV TPCH_DISTS_DSS=${TPCH_HOME}/dbgen/dists.dss
ENV TPCH_DSS_QUERY=${TPCH_HOME}/dbgen/queries
ENV DSS_QUERY=${TPCH_DSS_QUERY}

# TPC-DS
RUN aws --endpoint-url=${AWS_ENDPOINT_URL} --no-verify-ssl s3 cp s3://${S3_BUCKET}/tpc-ds/tpc-ds-tool-v4.0.0.zip . \
    && unzip tpc-ds-tool-v4.0.0.zip \
    && rm -f tpc-ds-tool-v4.0.0.zip \
    && cd tpc-ds-tool-v4.0.0/tools \
    && make LINUX_CFLAGS='-g -Wall -fcommon' \
    && chmod +x dsdgen dsqgen \
    && cp dsdgen dsqgen /usr/local/bin/

ENV TPCDS_HOME=/opt/tpc-benchmark/tpc-ds-tool-v4.0.0
ENV TPCDS_DISTRIBUTIONS=${TPCDS_HOME}/tools/tpcds.idx

# NVIDIA/spark-rapids-benchmarks
RUN git clone https://github.com/NVIDIA/spark-rapids-benchmarks.git \
    && cd spark-rapids-benchmarks/nds/tpcds-gen \
    && make clean all LINUX_CC='gcc -fcommon'  \
    && cd ../../nds-h/tpch-gen  \
    && make

ENTRYPOINT ["/bin/bash"]
