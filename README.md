# nba-rt-prediction
This repository holds code used to analyze NBA games and generate a model about how to predict game outcomes while games are in progress.  

If you would like to reproduce this work, you will need to setup an environment that supports
- spark 2.1
- Tensorflow 1.1 and Keras 
- brunel visualization

You can use Nimbix to get an environment that leverage GPU's running on IBM Power machines running Ubuntu 16.04
see this link to sign up for free 7 day trial 
https://developer.ibm.com/linuxonpower/cloud-resources/

Once you deploy the environment, you will need to install spark.  Here are the quick instructions 

## Environment Setup 
```
cd /data
git clone https://github.com/dustinvanstee/nba-rt-prediction.git
wget http://apache.claz.org/spark/spark-2.1.2/spark-2.1.2-bin-hadoop2.7.tgz 
tar -zxvf spark-2.1.2-bin-hadoop2.7.tgz
apt-get -y install openjdk-8-jdk

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-ppc64el
export SPARK_HOME=/data/spark-2.1.2-bin-hadoop2.7
```

## Start Jupyter
```
. /opt/DL/tensorflow/bin/tensorflow-activate
PYSPARK_DRIVER_PYTHON=jupyter PYSPARK_DRIVER_PYTHON_OPTS="notebook --ip=0.0.0.0 --allow-root --port=5050" $SPARK_HOME/bin/pyspark --master local[*]
```
