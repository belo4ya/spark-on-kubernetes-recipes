FROM spark:3.5.5-java17-python3

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    unzip \
    wget \
    awscli \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -P $SPARK_HOME/jars \
    && wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.783/aws-java-sdk-bundle-1.12.783.jar -P $SPARK_HOME/jars

WORKDIR /opt/tpc-benchmark

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_ENDPOINT_URL=https://s3.ru-7.storage.selcloud.ru
ARG S3_BUCKET=spark-benchmark

ENV AWS_ENDPOINT_URL=${AWS_ENDPOINT_URL}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV S3_BUCKET=${S3_BUCKET}

# Download and compile TPC-H tools
RUN aws --endpoint-url=${AWS_ENDPOINT_URL} --no-verify-ssl \
           s3 cp s3://${S3_BUCKET}/tpc-h/tpc-h-tool-v3.0.1.zip . \
    && unzip tpc-h-tool-v3.0.1.zip \
    && cd tpc-h-tool-v3.0.1/dbgen \
    && make -f makefile.suite CC=gcc MACHINE=LINUX WORKLOAD=TPCH DATABASE=ORACLE \
    && chmod +x dbgen qgen \
    && cp qgen dbgen /usr/local/bin/

ENV TPCH_DISTS_DSS=/opt/tpc-benchmark/tpc-h-tool-v3.0.1/dbgen/dists.dss
ENV TPCH_DSS_QUERY=/opt/tpc-benchmark/tpc-h-tool-v3.0.1/dbgen/queries
ENV DSS_QUERY=/opt/tpc-benchmark/tpc-h-tool-v3.0.1/dbgen/queries

ENTRYPOINT ["/bin/bash"]
