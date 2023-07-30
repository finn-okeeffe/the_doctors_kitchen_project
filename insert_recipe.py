# Commits new recipes to the db

from recipe_scraper import RecipeFactory, Recipe, Ingredient
import log
from typing import List, Tuple
import psycopg2 as pg2
import secret
from db_functions import DatabaseIdFields, Inserter

class RecipeInserter(Inserter):
    def __init__(self, cur):
        self.failed_recipes: List[Tuple[Recipe,int]] = []
        super().__init__(cur)


    def insert_recipe(self, recipeObject: Recipe) -> int:
        ## Attempts to insert the given recipe, and returns an exit code; these are as follows:
        # 1: successfully inserted to recipe table
        # 2: all of exit code 1 and inserted in meal table
        # 3: all of exit code 2 and inserted into ingredient table
        # 4: completed all insertions
        # 0: did not complete any insertions
        # -1: already in database
        # -2: not implemented
        log.log(f"Inserting recipe from url {recipeObject.url}")
        exit_code = 0
        if self.recipe_in_db(recipeObject):
            exit_code = -1
        else:
            try:
                # insert to recipe table
                log.log("Inserting into recipe table...")
                self.insert_into_recipe_table(recipeObject)
                exit_code = 1

                # insert into meal table
                log.log("Inserting into meal table...")
                self.insert_into_meal_table(recipeObject)
                exit_code = 2
                
                # insert to ingredient table
                log.log("Inserting into ingredient table...")
                self.insert_into_ingredient_table(recipeObject)
                exit_code = 3
                
                # insert to recipe_equipment table
                log.log("Inserting into recipe_equipment table...")
                log.log(f"equipment: {recipeObject.equipment}")
                self.insert_into_recipe_equipment_table(recipeObject)
                exit_code = 4

            except Exception as e:
                log.log(f"Insertion of recipe at url {recipeObject.url} failed: {e}")
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

