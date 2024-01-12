import logging
from sqlite3 import Error, Cursor
from string import ascii_lowercase
from typing import List, Dict
from pandas import DataFrame
import requests
from fractions import Fraction
import logging


def setup_logger(log_level: str = "INFO") -> logging.Logger:
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=log_format)
    log = logging.getLogger("drinks")
    log.setLevel(log_level)

    return log


def retrieve_drinks_list() -> List[List[Dict]]:
    """
    Function that reads the drinks associated to each letter of the alphabet (excluding the letters with no drinks)
    :return: Nested list containing dictionaries with the relative info and ingredients
    """
    drinks_list_raw = []
    for letter in list(ascii_lowercase):
        result = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}")
        if result.status_code == 200 and result.json()["drinks"] is not None:
            drinks_list_raw.append(result.json()["drinks"])
    return drinks_list_raw


def handle_query(cursor: Cursor, query: str, parameters: List = None) -> Cursor:
    """
    Execute a query inside a try - except block and return a cursor.
    :param cursor: Cursor to the database currently in use
    :param query: The query to be executed as a string
    :param parameters: Values to be substituted to '?' in a parametrized query
    :return: cursor containing the executed query
    """
    log = logging.getLogger("drinks")
    result = None
    try:
        if parameters:
            result = cursor.execute(query, parameters)
        else:
            result = cursor.execute(query)
    except Error as e:
        log.error(f"Error executing query: {query}.")
        log.error(e)
    return result


def to_dataframe(cursor: Cursor) -> DataFrame:
    """
    Transform an executed query with sqlite3 into a pandas DataFrame
    :param cursor: the object returned by a cursor.execute() statement
    :return: pandas DataFrame with the result of the query
    """
    columns = [column[0] for column in cursor.description]
    return DataFrame.from_records(cursor.fetchall(), columns=columns)


def measurement_conversion(measurement: str) -> str:
    """
        Convert a measurement in string to a string containing the equivalent in grams
            or the original measurement if not in oz, g, cl, shot, glass, tsp or tbsp
        :param measurement: string containing measurement
        :return: string containing grams equivalent or original measurement
    """
    conversion_map = {
        "oz": 28.3,
        "cl": 10,
        "ml": 1,
        "tblsp": 14.2,
        "tsp": 5.7,
        "cup": 240,
        "glass": 240,
        "can": 304.8,
        "drop": 0.05,
        "splash": 5.91,
        "shot": 44
    }
    if measurement:
        parts = measurement.split()
        if len(parts) >= 2:
            # Standardize the last 'word', assuming it's the unit of measure
            unit = parts[-1].lower()
            quantity_parts = parts[:-1]
            # Combine quantity parts, then convert to a float
            quantity_str = " ".join(quantity_parts)
            # I recognize as convertible units the ones with a number and/or a fraction
            #   and one word for unit of measurement. The rest is returned as is.
            try:
                quantity = sum(Fraction(part) for part in quantity_str.split()) if quantity_str else 1.0
                # Convert to grams if the unit is present in conversion_map, otherwise return original string
                for key in conversion_map:
                    if key in unit:
                        grams = quantity * conversion_map[key]
                        return f'{float(grams):.2f} g'
            except ValueError:
                pass
    return measurement
