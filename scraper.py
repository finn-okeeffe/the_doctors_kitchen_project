# Navigate and scrape recipes from The Doctors Kitchen
# Finn O'Keeffe - 2023-07-29

import requests
from bs4 import BeautifulSoup
from recipe_scraper import RecipeFactory, Recipe
from typing import List
from random import sample

class TheDoctorsKitchenScraper():

    sitemap_url = "https://thedoctorskitchen.com/sitemap.xml"
    recipe_url_list = []

    def __init__(self):
        self.recipeFactory = RecipeFactory()
        self.set_recipe_url_list()

    def set_recipe_url_list(self) -> List[str]:
        # parses the sitemap to return a list of recipe urls, to be used by n_random_recipes and all_recipes
        pass

    def n_random_recipes(self, n: int) -> List[Recipe]:
        # returns n distinct random recipe objects from the doctors kitchen
        if n > len(self.recipe_url_list):
            raise ValueError(f"Number of random samples n={n} larger than number of recipes {len(self.recipe_url_list)}")
        
        random_urls = sample(self.recipe_url_list, n)
        n_recipes = [self.recipeFactory.new_recipe(url) for url in random_urls]
        return n_recipes

    def all_recipes(self) -> List[Recipe]:
        all_recipes_list = [self.recipeFactory.new_recipe(url) for url in self.recipe_url_list]
        return all_recipes_list

if __name__ == "__main__":
    testScraper = TheDoctorsKitchenScraper()
    recipes = testScraper.n_random_recipes(5)
    for i,r in enumerate(recipes):
        print(f"{i}) {r.title}")
    