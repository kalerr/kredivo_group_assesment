-- DDL for the table

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

--1. Generate value of "Total equity and liabilities" from industry name "mining", "printing" and "construction"
-- Ans:
-- Below is query to get Total value for each industry. 
-- Resulting $275910000000000 for construction, $230114000000000 for mining and $16672000000000 for printing.
select "Industry_name_NZSIOC", sum(replace("Value",',','')::bigint)  * 1000000000 as Total
from annual_enterprise_survey aes 
where "Variable_name" = 'Total equity and liabilities'
	and lower("Industry_name_NZSIOC") in ('mining','printing','construction')
group by "Industry_name_NZSIOC";

-- Below is query to get Total value for mining, printing and construction industry. 
-- Resulting $522696000000000.
select sum(replace("Value",',','')::bigint)  * 1000000000 as Total
from annual_enterprise_survey aes 
where "Variable_name" = 'Total equity and liabilities'
	and lower("Industry_name_NZSIOC") in ('mining','printing','construction');

--2. Generate total value for all industry aggregation based on each variable name and units only Dollars
-- Ans:
-- There are 4 rows with 'C' as a Value. I couldnt get the meaning of 'C' in Value, so I exclude these 4 rows from the total.
-- These returns $679121000 for Total income per employee count and $104620200 for Surplus per employee count
select "Variable_name", sum(replace("Value",',','')::int) as Total
from annual_enterprise_survey aes 
where "Units" = 'Dollars'
	and "Value" <> 'C'
group by "Variable_name";

--3. Generate total value based on per individual industry name, per level and units only Dollars
-- Ans: Excluding value 'C', resulting in 128 rows of grouped Industry name and Level
select "Industry_name_NZSIOC" as "Industry Name", "Industry_aggregation_NZSIOC" as "Industry Level", sum(replace("Value",',','')::int) as Total
from annual_enterprise_survey aes 
where "Units" = 'Dollars'
	and "Value" <> 'C'
group by "Industry_name_NZSIOC", "Industry_aggregation_NZSIOC"
order by "Industry_name_NZSIOC", "Industry_aggregation_NZSIOC";


--4. Generate summary of yearly total values based on industry name and units only Dollars
-- Ans: Excluding value 'C', resulting in 856 rows of grouped Industry name and year
select "Industry_name_NZSIOC" as "Industry Name", "Year", sum(replace("Value",',','')::int) as Total
from annual_enterprise_survey aes 
where "Units" = 'Dollars'
	and "Value" <> 'C'
group by "Industry_name_NZSIOC", "Year";


--5. Generate top 3 and bottom 3 variable name in transposed format based on each year and units only Dollars
-- Ans: Using CTE to avoid querying the same table twice.
-- Using another CTE to only include rank 1, 2 and 3 from top and bottom.
-- Transposing in final select, making 1 2 3 as the column and year as the row
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