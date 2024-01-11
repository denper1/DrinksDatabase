create_drinks_table_query = """
CREATE TABLE IF NOT EXISTS drinks (
    drink_id INTEGER PRIMARY KEY,
    drink_name VARCHAR,
    tags VARCHAR,
    video_link VARCHAR,
    category VARCHAR,
    iba_category VARCHAR,
    is_alcoholic VARCHAR,
    glass VARCHAR,
    instructions VARCHAR,
    instructions_de VARCHAR,
    instructions_es VARCHAR,
    instructions_it VARCHAR,
    thumbnail_link VARCHAR,
    date_modified DATETIME
)
"""

create_ingredients_table_query = """
CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id INTEGER PRIMARY KEY,
    ingredient_name VARCHAR
    )
"""

create_measurements_table_query = """
CREATE TABLE IF NOT EXISTS measurements (
    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    drink_id INTEGER,
    ingredient_id INTEGER,
    measurement TEXT,
    original_measurement TEXT,
    FOREIGN KEY (drink_id) REFERENCES drinks(drink_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
)
"""

insert_into_drinks_query = """
INSERT INTO drinks (
    drink_id, drink_name, tags, video_link, category, iba_category, is_alcoholic, glass,
    instructions, instructions_de, instructions_es, instructions_it, thumbnail_link, date_modified)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

insert_into_ingredients_query = """
INSERT INTO ingredients (
    ingredient_id,
    ingredient_name)
VALUES (?, ?)
"""

insert_into_measurements_query = """
INSERT INTO measurements (
    drink_id, ingredient_id, measurement, original_measurement)
VALUES (?, ?, ?, ?)
"""

count_drinks_query = """
SELECT count(1) n_drinks FROM drinks"""

count_ingredients_query = """
SELECT count(1) n_ingredients FROM ingredients"""

count_measurements_query = """
SELECT count(1) as n_measurements FROM measurements"""


# Join drinks with measurements + ingredients twice so that we can have 2 ingredient_name columns
#   and apply the 2 different filters (ingredient = lemon and ingredient = whiskey).
# I use LIKE statements because the data is a bit dirty, the capitalization isn't super consistent
#   and there is a difference between 'whiskey' and 'whisky', plus 'Blended whiskey' is also used.
lemon_and_whiskey_cocktails_query = """
SELECT drinks.drink_name
FROM drinks
JOIN measurements ON drinks.drink_id = measurements.drink_id
JOIN ingredients AS lemon ON measurements.ingredient_id = lemon.ingredient_id
JOIN measurements AS whiskey_ingredient ON drinks.drink_id = whiskey_ingredient.drink_id
JOIN ingredients AS whiskey ON whiskey_ingredient.ingredient_id = whiskey.ingredient_id
WHERE lemon.ingredient_name LIKE '%emon' AND whiskey.ingredient_name LIKE '%hisk%'
GROUP BY drinks.drink_name"""

# Here is an alternative query where we join the tables only once, then we execute a DISTINCT on the groupings
#   to select only the drinks that have occurrences of both Lemon and Whiskey.
# After benchmarking the queries with timeit it appears the other query is slightly faster with the data
#   I downloaded, so I chose that one as the solution.
lemon_and_whiskey_cocktails_alternative_query = '''
    SELECT d.drink_name
    FROM drinks AS d
    JOIN measurements AS m ON d.drink_id = m.drink_id
    JOIN ingredients AS i ON m.ingredient_id = i.ingredient_id
    WHERE (i.ingredient_name LIKE '%emon' OR  i.ingredient_name LIKE '%hisk%')
    GROUP BY d.drink_name
    HAVING COUNT(DISTINCT i.ingredient_name) = 2
'''

# Check that the ingredients contain a version of "sambuca" and extract the numerical part from the grams
#   measurement (extract the string from the beginning to the third last character, thus excluding " g",
#   cast it as float and check that it's at least 15 g).
sambuca_cocktails_query = """
SELECT drink_name
FROM drinks as d
LEFT JOIN measurements as m on d.drink_id = m.drink_id
LEFT JOIN ingredients as i on m.ingredient_id = i.ingredient_id
WHERE i.ingredient_name LIKE '%ambuca%'
AND m.measurement LIKE '% g'
AND CAST(SUBSTR(m.measurement, 1, LENGTH(m.measurement) - 2) AS REAL) <= 15
GROUP BY d.drink_name
"""

# I rank the drinks by the count of the measurements. I use a RANK (instead of DENSE_RANK)
#   so that in case there are ties at #1 I return all the winners.
most_ingredients_drink_query = """
SELECT drink_name
FROM (
    SELECT drink_name, COUNT(m.measurement), RANK () OVER (ORDER BY COUNT(m.measurement) DESC) as ingredients_rank
    FROM drinks as d
    LEFT JOIN measurements as m ON d.drink_id = m.drink_id
    GROUP BY d.drink_id
)
WHERE ingredients_rank = 1"""

drop_table_query = "DROP TABLE {}"