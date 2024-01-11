import sqlite3
from itertools import chain

from resources.queries import (
    create_drinks_table_query,
    create_ingredients_table_query,
    create_measurements_table_query,
    insert_into_drinks_query,
    insert_into_ingredients_query,
    insert_into_measurements_query,
    count_drinks_query,
    count_ingredients_query,
    count_measurements_query,
    lemon_and_whiskey_cocktails_query,
    sambuca_cocktails_query,
    most_ingredients_drink_query
)
from resources.utils import (
    retrieve_drinks_list,
    handle_query,
    to_dataframe,
    measurement_conversion
)

db_name = "drinksdb"

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

all_drinks_list = retrieve_drinks_list()

# Create three tables for storing info about drinks, ingredients and the measurements of ingredients in each drink
drinks_table_creation = handle_query(cursor, create_drinks_table_query)
ingredients_table_creation = handle_query(cursor, create_ingredients_table_query)
measurements_table_creation = handle_query(cursor, create_measurements_table_query)

# I create a drink ingredients hashtable to keep tabs on the ingredients already added in the table
#   and to keep track of their IDs (stored in 'ingredients_counter')
drink_ingredients_dict = {}

ingredients_counter = 1
for drink in chain.from_iterable(all_drinks_list):
    if drink["strInstructionsDE"]:
        # Insert drink
        drink_arguments = [drink["idDrink"], drink["strDrink"], drink["strTags"], drink["strVideo"],
                           drink["strCategory"], drink["strIBA"], drink["strAlcoholic"], drink["strGlass"],
                           drink["strInstructions"], drink["strInstructionsDE"], drink["strInstructionsES"],
                           drink["strInstructionsIT"], drink["strDrinkThumb"], drink["dateModified"]]
        drink_insertion = handle_query(cursor, insert_into_drinks_query, drink_arguments)
        # Insert ingredients
        drink_counter = 1
        # While loop with counter to insert ingredients because a drink hardly ever has the max ingredients allowed (15)
        while drink[f"strIngredient{drink_counter}"]:
            ingredient_name = drink[f"strIngredient{drink_counter}"]
            ingredient_id = drink_ingredients_dict.get(ingredient_name, None)
            # If the ingredient has already been inserted there's no need to reinsert it
            if not ingredient_id:
                drink_ingredients_dict[ingredient_name] = ingredients_counter
                ingredient_insertion = handle_query(
                    cursor, insert_into_ingredients_query, [ingredients_counter, ingredient_name]
                )
                ingredients_counter += 1
            # Insert measurement in a separate table for normalization
            original_measurement = drink[f"strMeasure{drink_counter}"]
            converted_measurement = measurement_conversion(original_measurement)
            measurement_arguments = [
                drink["idDrink"], drink_ingredients_dict[ingredient_name], converted_measurement, original_measurement
            ]
            measurement_insertion = handle_query(cursor, insert_into_measurements_query, measurement_arguments)
            drink_counter += 1

drinks = handle_query(cursor, count_drinks_query)
print("Number of drinks inserted: ")
print(to_dataframe(drinks))

ingredients = handle_query(cursor, count_ingredients_query)
print("Number of ingredients inserted: ")
print(to_dataframe(ingredients))

measurements = handle_query(cursor, count_measurements_query)
print("Number of measurements inserted: ")
print(to_dataframe(measurements))

# Which alcoholic drinks can be mixed with lemon and whiskey?
lemon_and_whiskey = handle_query(cursor, lemon_and_whiskey_cocktails_query)
print("Which alcoholic drinks can be mixed with lemon and whiskey?")
print(to_dataframe(lemon_and_whiskey))

# Which drink(s) can be mixed with just 15g of Sambuca?
sambuca_cocktails = handle_query(cursor, sambuca_cocktails_query)
print("Which drink(s) can be mixed with just 15g of Sambuca?")
print(to_dataframe(sambuca_cocktails).to_string())

# 3. Which drink has the most ingredients?
most_ingredients = handle_query(cursor, most_ingredients_drink_query)
print(" Which drink has the most ingredients?")
print(to_dataframe(most_ingredients).to_string())

cursor.close()
conn.close()
