# Commits new recipes to the db
# Finn O'Keeffe - 28/07/2023

from recipe_scraper import RecipeFactory, Recipe, Ingredient
import log
from typing import List, Tuple
import psycopg2 as pg2
import secret

class RecipeInserter():
    def __init__(self, cur):
        self.cur: pg2.cursor = cur
        self.failed_recipes: List[Tuple[Recipe,int]] = []

    def insert_recipe(self, recipeObject: Recipe) -> int:
        ## Attempts to insert the given recipe, and returns an exit code; these are as follows:
        # 1: success
        # -1: already in database
        # -2: not implemented
        # -10: unknown error

        if self.recipe_in_db(recipeObject):
            exit_code = -1
        else:
            try:
                # insert to recipe table

                # insert to recipe_equipment table
                
                # insert to ingredient table

                exit_code = -2
            except Exception as e:
                exit_code = -10
                log.log(f"Insertion of recipe at url {url} failed: {e}")
        self.failed_recipes.append((recipeObject, exit_code))
        return exit_code
    
    def recipe_in_db(self, recipeObject: Recipe) -> bool:
        self.cur.execute("SELECT id FROM recipe WHERE url=%s",(recipeObject.url,))
        results = self.cur.fetchall()
        if len(results) != 0:
            log.log(f"Insertion failed: already in database with recipe.id {results[0][0]} - url: {recipeObject.url}")
            return False



def insert_recipes(recipes_list: List[Recipe]):
    with pg2.connect(database=secret.database_name, user=secret.username, password=secret.password) as conn:
        with conn.cursor() as cur:
            inserter = RecipeInserter(cur)
            for recipe in recipes_list:
                inserter.insert_recipe(recipe)

if __name__ == "__main__":
    log.logging = True
    recipeFactory = RecipeFactory()

    test_urls = ["https://thedoctorskitchen.com/recipes/smoky-mushroom-and-tempeh-veggie-burgers/"]
    recipe_list = []
    for url in test_urls:
        recipe_list.append(recipeFactory.new_recipe(url))
    
    insert_recipes(recipe_list)

