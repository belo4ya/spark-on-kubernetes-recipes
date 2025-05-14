FROM spark:3.5.5-java17

RUN apt-get update && apt-get install -y \
    build-essential unzip wget awscli git \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -P $SPARK_HOME/jars \
    && wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.783/aws-java-sdk-bundle-1.12.783.jar -P $SPARK_HOME/jars
