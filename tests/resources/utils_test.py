import pytest
from unittest.mock import patch, MagicMock, call
from resources.utils import (
    retrieve_drinks_list,
    handle_query,
    to_dataframe,
    measurement_conversion
)
from string import ascii_lowercase
from pandas import DataFrame
from sqlite3 import Error


@pytest.mark.parametrize("letter, status_code, expected_result",
                         [
                             ('a',
                              200,
                              [
                                  {'drink_name': 'Margarita'},
                                  {'drink_name': 'Martini'}
                              ]
                              ),
                         ]
                         )
def test_retrieve_drinks_list(letter, status_code, expected_result):
    with patch('requests.get') as mock_get:
        # Create a MagicMock for the result of requests.get
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {'drinks': [{'drink_name': 'Margarita'}, {'drink_name': 'Martini'}]}

        # Set the return value of the MagicMock to the mock_response
        mock_get.return_value = mock_response

        # Call the function to be tested
        result = retrieve_drinks_list()

        # Assert the result matches the expected result for each letter
        assert result == [expected_result] * 26  # Repeat the expected result 26 times

        # Assert that requests.get was called with the correct URL 26 times (once for each letter)
        expected_calls = [call(f"https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}") for letter in ascii_lowercase]
        mock_get.assert_has_calls(expected_calls, any_order=True)  # Allow calls in any order



def test_handle_query():
    # Create a mock cursor and execute a query
    cursor_mock = MagicMock()
    handle_query(cursor_mock, "SELECT * FROM the_table")
    # Verify that the execute method was called with the correct query
    cursor_mock.execute.assert_called_once_with("SELECT * FROM the_table")


def test_query_execution_with_parameters():
    # Mock the execute method to simulate query execution with parameters
    cursor = MagicMock()
    mock_rowcount = MagicMock(return_value=1)
    cursor.execute = MagicMock(return_value=cursor)
    cursor.rowcount = mock_rowcount

    query = 'INSERT INTO test_table (name) VALUES (?)'
    parameters = ('TestName',)
    result = handle_query(cursor, query, parameters)
    assert result is not None
    assert result.rowcount.return_value == 1


def test_handle_query_failure():
    cursor = MagicMock()
    cursor.execute = MagicMock(side_effect=Error('Test error'))

    query = 'INSERT INTO non_existing_table (name) VALUES (?)'
    parameters = ('TestName',)
    result = handle_query(cursor, query, parameters)
    assert result is None  # Expecting None due to an error


def test_to_dataframe():
    # Create a mock cursor and execute a query
    cursor_mock = MagicMock()
    cursor_mock.description = [('id',), ('name',)]
    cursor_mock.fetchall.return_value = [(1, 'Foo'), (2, 'Bar')]
    result = to_dataframe(cursor_mock)
    # Verify that the DataFrame is created correctly
    assert result.equals(DataFrame({'id': [1, 2], 'name': ['Foo', 'Bar']}))


@pytest.mark.parametrize("measurement, expected_result", [
    ('2 oz', '56.60 g'),
    ('1 1/2 cl ', '15.00 g'),
    ('3 tblsp', '42.60 g'),
    ('1 tsp ', '5.70 g'),
    ('1 cup', '240.00 g'),
    ('', ''),
    # Add more test cases as needed
])
def test_measurement_conversion(measurement, expected_result):
    result = measurement_conversion(measurement)
    assert result == expected_result
