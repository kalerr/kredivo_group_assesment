# Data Engineer & Analytic assessment at Kredivo Group

Welcome to my repository for the Data Engineer & Analytic assessment at Kredivo Group. This project demonstrates a simple SQL, Web Crawling and System Architecture design.

## Prerequisites

Before you begin, ensure you have the following:

- **PostgreSQL** hosted locally
- **Python and Conda** to run the web crawling and manage environment
  - Create a Conda environment by going to the directory of the repository and activate
    ```
      cd /FinAccel\ -\ Data Engineer\ and\ Analytics\ Test\ Case/answer/2.\ Web\ Crawling
      conda env create -f environment.yml
      conda activate kredive_test_de
    ```
- **Optional DBeaver** for easier querying and import

## SQL
0. **Create a table**
   ```
        create schema kredivo_de;

        create table kredivo_de.annual_enterprise_survey (
            "Year" int4 null,
            "Industry_aggregation_NZSIOC" varchar(250) null,
            "Industry_code_NZSIOC" varchar(250) null,
            "Industry_name_NZSIOC" varchar(250) null,
            "Units" varchar(250) null,
            "Variable_code" varchar(250) null,
            "Variable_name" varchar(250) null,
            "Variable_category" varchar(250) null,
            "Value" varchar(250) null,
            "Industry_code_ANZSIC06" varchar(250) null
        );
    ```
  Import the data. We are using DBeaver.
   ![alt text](/img/dbeaver%20import.jpeg)

1. **Generate value of "Total equity and liabilities" from industry name "mining", "printing" and "construction"**
   - Below is the query to get Total value for each industry. 
   - Resulting $275910000000000 for construction, $230114000000000 for mining and $16672000000000 for printing.
     ```
      select "Industry_name_NZSIOC", sum(replace("Value",',','')::bigint)  * 1000000000 as Total
      from annual_enterprise_survey aes 
      where "Variable_name" = 'Total equity and liabilities'
          and lower("Industry_name_NZSIOC") in ('mining','printing','construction')
      group by "Industry_name_NZSIOC";
     ```
     ![alt text](/img/sql_1_a.png)
   - Below is query to get Total value for mining, printing and construction industry. 
   - Resulting $522696000000000.
     ```
      select sum(replace("Value",',','')::bigint)  * 1000000000 as Total
      from annual_enterprise_survey aes 
      where "Variable_name" = 'Total equity and liabilities'
          and lower("Industry_name_NZSIOC") in ('mining','printing','construction');
     ```
     ![alt text](/img/sql_1_b.png)

2. **Generate total value for all industry aggregation based on each variable name and units only Dollars**
   - There are 4 rows with 'C' as a Value. I couldnt get the meaning of 'C' in Value, so I exclude these 4 rows from the total. 
   - These returns $679121000 for Total income per employee count and $104620200 for Surplus per employee count
     ```
      select "Variable_name", sum(replace("Value",',','')::int) as Total
      from annual_enterprise_survey aes 
      where "Units" = 'Dollars'
          and "Value" <> 'C'
      group by "Variable_name";
     ```
     ![alt text](/img/sql_2.png)

3. **Generate total value based on per individual industry name, per level and units only Dollars**
   - Excluding value 'C', resulting in 128 rows of grouped Industry name and Level
     ```
      select "Industry_name_NZSIOC" as "Industry Name", "Industry_aggregation_NZSIOC" as "Industry Level", sum(replace("Value",',','')::int) as Total
      from annual_enterprise_survey aes 
      where "Units" = 'Dollars'
          and "Value" <> 'C'
      group by "Industry_name_NZSIOC", "Industry_aggregation_NZSIOC"
      order by "Industry_name_NZSIOC", "Industry_aggregation_NZSIOC";
     ```
     ![alt text](/img/sql_3.png)

4. **Generate total value for all industry aggregation based on each variable name and units only Dollars**
   - Generate summary of yearly total values based on industry name and units only Dollars
   - Excluding value 'C', resulting in 856 rows of grouped Industry name and year
     ```
      select "Industry_name_NZSIOC" as "Industry Name", "Year", sum(replace("Value",',','')::int) as Total
      from annual_enterprise_survey aes 
      where "Units" = 'Dollars'
          and "Value" <> 'C'
      group by "Industry_name_NZSIOC", "Year";
     ```
     ![alt text](/img/sql_4.png)

5. **Generate total value for all industry aggregation based on each variable name and units only Dollars**
   - Using CTE to avoid querying the same table twice.
   - Using another CTE to only include rank 1, 2 and 3 from top and bottom.
   - TTransposing in final select, making 1 2 3 as the column and year as the row
     ```
      with cte as (
      select 
          "Variable_name", 
          "Year",
          row_number() over (partition by "Year" order by replace("Value",',','')::int desc) as top_rank,
          row_number() over (partition by "Year" order by replace("Value",',','')::int asc) as bot_rank
      from annual_enterprise_survey aes 
      where "Units" = 'Dollars'
          and "Value" <> 'C'
      ),
      top_bottom as (
      select 
          "Variable_name", 
          "Year",
          'top' as rank_type,
          top_rank as rank
      from cte
      where top_rank <= 3
      union all
      select 
          "Variable_name", 
          "Year",
          'bottom' as rank_type,
          bot_rank as rank
      from cte
      where bot_rank <= 3
      )
      select 
      "Year",
      max(case when rank_type = 'top' and rank = 1 then "Variable_name" end) as top_1,
      max(case when rank_type = 'top' and rank = 2 then "Variable_name" end) as top_2,
      max(case when rank_type = 'top' and rank = 3 then "Variable_name" end) as top_3,
      max(case when rank_type = 'bottom' and rank = 1 then "Variable_name" end) as bottom_1,
      max(case when rank_type = 'bottom' and rank = 2 then "Variable_name" end) as bottom_2,
      max(case when rank_type = 'bottom' and rank = 3 then "Variable_name" end) as bottom_3
      from top_bottom
      group by 
      "Year"
      order by 
      "Year";
     ```
     ![alt text](/img/sql_5.png)

## Web Crawling
   - We are using Selenium and bs4 to get data from Tokopedia, extracting Xiaomi's wearable device, tablet and handphone category. We extract 2 pages of data per category
   - To run the script, make sure you have the environment activated in conda. Then run the script by
    python answer/2.\ Web\ Crawling/main.py
   - Wait until the driver is closed, then you can check the csv and json in 'Web Crawling' folder.
  ![alt text](/img/tokped.png)
  
## Movflix Architecture
   1. ![alt text](/img/Movflix_Architecture.png)
   Flow:

   - a. Data Collection
   User activity and ratings are collectted from the app (deployed by Google Kubernetes Engine (GKE)) and sent to Apigee. 
   Apigee then send this data to Pub/Sub topic. These data includes links, movies, ratings, tags.

   - b. Data Ingestion
   Pubsub publish message to triggger cloud function, then store raw data to Google Cloud Storage (GCS). 
   Data sent to GCS in csv format, is a not frequently accessed data and will be used as a training data, such as tags.
   For real time data, we use Dataflow to get data from Pub/Sub for real-time batch processing and transforming. 
   Processed data will be stored in Google BigQuery (GBQ).

   - c. Data Processing
   Batch processing will be done in Dataflow, creating a set of variables that can be used for training the model and stored at GBQ.

   - d. Model Training
   BigQuery ML or Vertex AI trains a recommendation model using processed data from GBQ and GCS. 
   Recommendation will mainly use ratings and user profile(not available in provided csv).

   - e. Real-time serving 
   Generated recommendation will be uploaded to firestore using a scheduled cloud function, getting data from GBQ.
   Now Movflix application will fetch recommendations from firestore.

   2.
   Pro: 
       - Scalability, the system will not have problem handling an increasing amount of data.
       - Integrated, fully built on GCP ecosystem
       - User Experience, real time recommendation with firebase
   Cons: 
       - Cost management, using multiple service at once will need a good cost management.
       - Complexity, using multiple service will add the complexity of the architecture and it will increase the learning curve

   3. 
   Rating based algorithm, which mean we highly depends on rating since we do not have user watch history yet