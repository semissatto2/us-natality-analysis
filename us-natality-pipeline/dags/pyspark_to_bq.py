from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import broadcast

# Define constants
BUCKET_DATAPROC = "dataproc-temp-us-central1-1024460416669-nwawz3vd"  # TODO: Insert input here
BUCKET_NATALITY = "gs://us-natality-bucket/natality/*"  # TODO: Insert input here
BUCKET_LOOKUP_RACE = "gs://us-natality-bucket/natality-lookup_tables/race_lookup.csv"  # TODO: Insert input here
BUCKET_LOOKUP_STATE = "gs://us-natality-bucket/natality-lookup_tables/state_lookup.csv"  # TODO: Insert input here
GCP_BIGQUERY_DATASET = "us_natality_dataset"  # TODO: Insert input here
OUTPUT = f"{GCP_BIGQUERY_DATASET}.natality"

def main():
    # Initialize Spark session
    spark = (
        SparkSession.builder
        .appName("natality_data_processing")
        .getOrCreate()
    )
    
    spark.conf.set("temporaryGcsBucket", BUCKET_DATAPROC)
    
    # Load natality data
    df = spark.read.csv(BUCKET_NATALITY, header=True, inferSchema=True)
    
    # Load and broadcast lookup tables
    df_lk_race = broadcast(spark.read.csv(BUCKET_LOOKUP_RACE, header=True, inferSchema=True))
    df_lk_state = broadcast(spark.read.csv(BUCKET_LOOKUP_STATE, header=True, inferSchema=True))
    
    # Join natality data with lookup tables
    df = (
        df
        .join(df_lk_race, df["child_race"] == df_lk_race["child_race_id"], "left")
        .join(df_lk_state, df["state"] == df_lk_state["Code"], "left")
        .drop(df.state)
        .drop(df_lk_state.Code)
        .drop(df_lk_race.child_race_id)
        .withColumnRenamed("State", "state_name")
        .withColumn("gestation_weeks", F.col("gestation_weeks").cast("int"))
        .select("year", "month", "child_race", "child_race_name", "state_name", "is_male", "gestation_weeks", "weight_pounds")
    )
    # Register temporary SQL table
    df.createOrReplaceTempView("natality")
    
    # Aggregate natality data
    df_agg_natality = spark.sql(
        """
        SELECT
            year,
            month,
            child_race,
            child_race_name,
            state_name,
            is_male,
            COUNT(*) AS total_count
        FROM natality
        GROUP BY year, month, child_race, child_race_name, state_name, is_male
        ORDER BY year ASC, month DESC
        """
    )
    
    # Aggregate gestation data
    df_agg_gestation = spark.sql(
        """
        SELECT
            gestation_weeks,
            is_male,
            AVG(weight_pounds) AS avg_weight_pounds,
            COUNT(*) AS total_count
        FROM natality
        GROUP BY gestation_weeks, is_male
        ORDER BY gestation_weeks ASC
        """
    )
    
    # Write data to BigQuery
    df.write \
        .format("bigquery") \
        .option("table", OUTPUT) \
        .option("clusteringFields", "year") \
        .mode("overwrite") \
        .save()
    
    df_agg_natality.write \
        .format("bigquery") \
        .option("table", OUTPUT + "_agg") \
        .option("clusteringFields", "year") \
        .mode("overwrite") \
        .save()
    
    df_agg_gestation.write \
        .format("bigquery") \
        .option("table", OUTPUT + "_gestation_agg") \
        .mode("overwrite") \
        .save()

if __name__ == "__main__":
    main()
