"""CSC111 Project 2: The Ultimate Recipe Index - File Reader

===============================

This Python module contains code meant to read from parquet files and CSV files, then clean the
data to make it usable for the program
"""

from __future__ import annotations

import re
import csv

import pandas as pd
import pyarrow
import fastparquet

UID_INDEX = 0
NAME_INDEX = 1
STEPS_INDEX = 2
INGREDIENTS_INDEX = 3
CATEGORIES_INDEX = 4
NAME_TOKENS_INDEX = 5

BASE_INDEX = 0
TARGET_INDEX = 1
NAME_OVERLAP_INDEX = 2
NAME_SIMILARITY_INDEX = 3

OPEN_MODE = 'r'
PARQUET_EXTENSION = '.parquet'
CSV_EXTENSION = '.csv'

START_BRACKET, CLOSE_BRACKET = '[', ']'
UNWANTED_VALUES_REGEX = r"'([^']*)'|\"([^\"]*)\""


def read_recipes_data(path: str, is_csv: bool) -> list[list]:
    """
    Reads data from the recipe data file and returns a tidy list of the data.

    Each row represents a recipe, with each row looking like:
    [recipe_id, name, steps, ingredients, categories, name_tokens], where
    - recipe_id is an int of the id of the recipe
    - name is a string of the name of the recipe
    - steps is a string of the steps of this recipe
    - ingredients are the ingredients contained within the recipe, list of strings
    - categories is the categories this recipe belongs to, list of strings
    - name_tokens is a list of every word in the name

    NOTE: after being cleaned, the ingredients, categories, and name_tokens all follow
    a lowercase format which turns strings like 'LOW_Sugar' -> 'low sugar'

    Preconditions:
        - path is the path to the parquet of the recipes data
    """
    lst = read_csv(path) if is_csv else read_parquet(path)
    return clean_recipe_data(lst)


def read_pairs_data(path: str, is_csv: bool) -> list[list]:
    """
    Reads data from the pairs data file and returns a tidy list of the data.

    Each row represents a recipe pair, with each row looking like
    [base, target, name_overlap, name_similarity, categories], where:
    - base is the recipe which we are using as the replacement
    - target is the recipe being replaced
    - name_overlap is a string of the name overlap between the two recipes
    - name_similarity is a double form 0-1 of how similar in terms of name the recipes are
    - categories is a list of the catgeories which the replacement satisfies
    Preconditions:
        - path is the path to a csv/parquet of pairs data
    """
    lst = read_csv(path) if is_csv else read_parquet(path)
    return clean_pairs_data(lst)


def read_parquet(path: str) -> list[list[str]]:
    """
    Reads data from a given parquet file path and returns a raw list of data.

    Preconditions:
        - path is a valid file path to a parquet file
    """
    return read_csv(parquet_to_csv(path))


def read_csv(path: str) -> list[list[str]]:
    """
    Reads data from a given csv file path and returns a raw list of data.

    Preconditions:
        - path is a valid file path to a csv file
    """
    with open(path, OPEN_MODE, encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        return list(reader)


def parquet_to_csv(path: str) -> str:
    """
    Turns the given parquet file to a csv file and returns the path to the csv file

    Preconditions:
        - path is a valid file path to a parquet file
    """
    data = pd.read_parquet(path)
    csv_path = path.replace(PARQUET_EXTENSION, CSV_EXTENSION)
    data.to_csv(csv_path, index=False)
    return csv_path


def clean_recipe_data(lst: list[list]) -> list[list]:
    """
    Cleans the given list by turning every non-numeric element into a lowercase string of characters with no
    non-alphabetical characters
    """
    clean_lst = []
    for row in lst:
        recipe_id = int(row[UID_INDEX])
        name = row[NAME_INDEX]
        steps = row[STEPS_INDEX]
        ingredients = process_varchar_list(row[INGREDIENTS_INDEX])
        categories = process_varchar_list(row[CATEGORIES_INDEX])
        name_tokens = process_varchar_list(row[NAME_TOKENS_INDEX])
        clean_lst.append([recipe_id, name, steps, ingredients, categories, name_tokens])
    return clean_lst


def clean_pairs_data(lst: list[list]) -> list[list]:
    """
    Cleans the given list by turning every non-numeric element into a lowercase string of characters with no
    non-alphabetical characters
    """
    clean_lst = []
    for row in lst:
        base = int(row[BASE_INDEX])
        target = int(row[TARGET_INDEX])
        name_overlap = row[NAME_OVERLAP_INDEX]
        name_similarity = float(row[NAME_SIMILARITY_INDEX])
        categories = process_varchar_list(row[CATEGORIES_INDEX])
        clean_lst.append([base, target, name_overlap, name_similarity, categories])
    return clean_lst


def process_varchar_list(lst: str) -> list[str]:
    """
    Convert a string representation of a list into a Python list.
    Handles both:
    - ['a', 'b', 'c']
    - ['a' 'b' 'c']
    """
    if not lst:
        return []

    value = lst.strip()

    if value.startswith(START_BRACKET) and value.endswith(CLOSE_BRACKET):
        value = value[1:-1]

    matches = re.findall(UNWANTED_VALUES_REGEX, value)
    result = [(m[0] or m[1]).replace("_", " ") for m in matches]

    return result
