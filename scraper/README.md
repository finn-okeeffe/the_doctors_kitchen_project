# Scraper

This file contains the code to:
- scrape data from [The Doctors Kitchen](https://thedoctorskitchen.com/)
- clean the data
- apply NLP to obtain the equipment used for the recipe
- insert the data into the remote database.

## Connecting to the database:
Inserting into the database requires a secret.py file, containing the database host, user, etc. It is formatted as follows:
```python
connection_kw_args = {
    'user': '...',
    'password': '...',
    'database': '...',
    'host': '...',
    'port': '...'
}
```
This dictionary is passed as keyword arguments to [psycopg2.connect](https://www.psycopg.org/docs/module.html) as follows:
```python
import secret
import psycopg2 as pg2

with conn as pg2.connect(**secret.connection_kw_args):
    ...
```
So the secret dictionary can contain any arguments used in the connection function.

## drs_kitchen_scraping_poc.ipynb
This file was an initial proof of concept I constructed when I was first thinking about this project. I used it to see what information I could get from each recipe page.

## db_functions.py
This file contains functions to interact with the database. Such as a class to hold ID dictionaries, and a class to manage inserting information into the database.

## equipment_parser.py
This file parses the text contained in the recipe to obtain a list of equipment required from the recipe.
It does this by searching the text in a recipe certain phrases which indicate the use of a specific piece of equipment. These phrases are contained in the dictionary `equipment_dict`, with their names as the keys.
Before using other files you must run the function `load_equipment_dict` to fetch the dictionary.
To obtain a list of equipment used in a recipe, we call `equipment_set(method: List[str], ingredient_strings: List[str])`,
which returns a set of strings of the equipment used in the recipe.

## recipe_classes.py
Throughout this folder, I store ingredients in `Ingredient` objects, and recipes in `Recipe` objects. This file contains the definitions of these classes.

## recipe_scraper.py
This file contains methods to scrape and parse a single recipe from a given url.
It contains the classes `IngredientListFactory` and `RecipeFactory` to create the objects associated with the recipe.

## scraper.py
This file contains the class `TheDoctorsKitchenScraper`. This class contains methods to navigate the website using its [sitemap](https://thedoctorskitchen.com/sitemap.xml),
and constructs recipes by calling methods from `recipe_scraper.py`. There are two control methods:
- `TheDoctorsKitchenScraper.n_random_recipes(n: int)`: scrapes `n` random recipes, returning a list of `n` recipe objects.
- `TheDoctorsKitchenScraper.all_recipes()`: Scrapes all recipes, returning a list of recipe objects.

Lastly, when ran as a program this file calls functions from `insert_recipe.py` to insert the recipe objects into the database.

## insert_recipe.py
Contains `RecipeInserter`, used to insert a Recipe object into the database. Also contains the function `insert_recipes` used to insert a list of Recipe objects.

## log.py
Contains functions and parameters used for logging and progress indication.

## initial_equipment_insert
A script I used to insert my initial equipment dictionary into the database.

## update_equipment_tables.py
A script used to re-process the recipe text to get the equipment used in each recipe, then insert these results into the database.
Currently this is a little bit of a pain to use for the following reasons:
- You must update the `equipment` and `equipment_synonym` tables in the database first, inserting any new equipment and phrases you want.
- The script is inefficient. It deletes every entry from `recipe_equipment`, then inserts each all the new rows in individual queries. To improve this I should:
  - Use the `comparison_test` function to only delete and insert rows that need it.
  - Insert rows using a single `INSERT INTO` query.
