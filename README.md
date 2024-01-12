# Drinks Database

This repository is for the exercise _drinks database_ , which downloads as many drinks from the [Cocktail DB API](https://www.thecocktaildb.com/api.php), loads the data in a relational database and answers some queries on the drinks.

## Installation

The installation process for the environment is automated in the Makefile.
````
make init
````

## Execution

To execute the script run: 

````
python drinks_database.py
````

or

````
make execute
````

To clear the tables:

````
make drop-tables
````
