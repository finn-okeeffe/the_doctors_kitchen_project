# Commits new recipes to the db
# Finn O'Keeffe - 28/07/2023

from recipe_scraper import RecipeFactory, Recipe, Ingredient
import log
from typing import List
import psycopg2 as pg2
import secret

class RecipeInserter():
    def __init__(self, cur):
        self.cur = cur
        self.failed_urls = []

    def insert_recipe(self, recipeObject: Recipe) -> bool:
        success = False
        if not(success):
            self.failed_urls.append(recipeObject.url)
            log.log(f"Insertion failed: not implemented - url: {recipeObject.url}")
        return success
    
def insert_recipes(recipes_list: List[Recipe]):
    with pg2.connect(database="the_doctors_kitchen", user=secret.username, password=secret.password) as conn:
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

