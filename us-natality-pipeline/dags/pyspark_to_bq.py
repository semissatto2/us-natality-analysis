#!/usr/bin/env python
# coding: utf-8

import pyspark
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types

BUCKET_DATAPROC = 'dataproc-temp-us-central1-1024460416669-nwawz3vd' # TODO: insert bucket created by dataproc here
BUCKET_NATALITY = 'gs://us-natality-bucket/natality/*' # TODO: insert name of bucket here
GCP_BIGQUERY_DATASET = 'us_natality_dataset' # TODO: insert name of dataset here
OUTPUT = GCP_BIGQUERY_DATASET + '.' + 'natality'
print('Hello from Dataproc')

# schema = types.StructType([
#     types.StructField('Wave', types.StringType(), True), 
#     types.StructField('SiteID', types.StringType(), True), 
#     types.StructField('Date', types.StringType(), True), 
#     types.StructField('Weather', types.StringType(), True), 
#     types.StructField('Time', types.StringType(), True), 
#     types.StructField('Day', types.StringType(), True), 
#     types.StructField('Round', types.StringType(), True), 
#     types.StructField('Direction', types.StringType(), True), 
#     types.StructField('Path', types.StringType(), True), 
#     types.StructField('Mode', types.StringType(), True), 
#     types.StructField('Count', types.LongType(), True)
# ])

spark = SparkSession.builder \
    .appName('test') \
    .getOrCreate()

spark.conf.set('temporaryGcsBucket', BUCKET_DATAPROC)

df = spark.read.csv(BUCKET_NATALITY, header=True, inferSchema=True)

# df_2023 = df_2023.withColumn('Year', F.lit('2023'))

# df_2024 = spark.read.csv(input_2024, header=True, schema=schema)

# df_2024 = df_2024.withColumn('Year', F.lit('2024'))

# df_all = df_2023.unionAll(df_2024)

# df_all.createOrReplaceTempView("cycling_data")

# df_result = spark.sql('''
# SELECT
#     Year,
#     SiteID,
#     Weather,
#     Direction,
#     Path,
#     Mode,
#     SUM(Count) AS Total_Count,  -- Total traffic count
#     AVG(Count) AS Avg_Count,    -- Average traffic count per record
#     MAX(Count) AS Max_Count,    -- Maximum traffic count recorded
#     MIN(Count) AS Min_Count     -- Minimum traffic count recorded
# FROM cycling_data
# GROUP BY Year, SiteID, Weather, Direction, Path, Mode
# ORDER BY Year, SiteID
# ''')

df.write \
        .format("bigquery") \
        .option("table", OUTPUT) \
        .save()