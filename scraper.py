# Navigate and scrape recipes from The Doctors Kitchen
# Finn O'Keeffe - 2023-07-29

import requests
from bs4 import BeautifulSoup
from recipe_scraper import RecipeFactory, Recipe
from typing import List
from random import sample
from insert_recipe import insert_recipes
import log
from tqdm import tqdm

class TheDoctorsKitchenScraper():

    sitemap_url = "https://thedoctorskitchen.com/sitemap.xml"
    recipe_url_start = "https://thedoctorskitchen.com/recipes/"
    url_starts_to_ignore = [
        "https://thedoctorskitchen.com/recipes/breakfast/",
        "https://thedoctorskitchen.com/recipes/lunch/",
        "https://thedoctorskitchen.com/recipes/snack/",
        "https://thedoctorskitchen.com/recipes/dinner/"
    ]
    recipe_url_list = []

    def __init__(self):
        self.recipeFactory = RecipeFactory()
        self.set_recipe_url_list()

    def set_recipe_url_list(self):
        # parses the sitemap to return a list of recipe urls, to be used by n_random_recipes and all_recipes
        sitemap_xml = requests.get(self.sitemap_url)
        sitemap_soup = BeautifulSoup(sitemap_xml.content, "xml")
        all_urls = [loc.text.strip() for loc in sitemap_soup.find_all("loc")]
        for url in all_urls:
            if self.is_recipe_page(url):
                self.recipe_url_list.append(url)
        log.log(f"loaded {len(self.recipe_url_list)} recipe URLs")

    def is_recipe_page(self, url: str) -> bool:
        page_is_recipe = self.recipe_url_start in url
        for address in self.url_starts_to_ignore:
            page_is_recipe = page_is_recipe and not(address in url)
        
        return page_is_recipe

    def n_random_recipes(self, n: int) -> List[Recipe]:
        # returns n distinct random recipe objects from the doctors kitchen
        if n > len(self.recipe_url_list):
            raise ValueError(f"Number of random samples n={n} larger than number of recipes {len(self.recipe_url_list)}")
        
        random_urls = sample(self.recipe_url_list, n)

        if log.log_progress:
            iterator = tqdm(random_urls)
        else:
            iterator = random_urls

        n_recipes = []
        for url in iterator:
            n_recipes.append(self.recipeFactory.new_recipe(url))
        return n_recipes

    def all_recipes(self) -> List[Recipe]:
        if log.log_progress:
            iterator = tqdm(self.recipe_url_list)
        else:
            iterator = self.recipe_url_list

        all_recipes_list = []
        for url in iterator:
            all_recipes_list.append(self.recipeFactory.new_recipe(url))
        return all_recipes_list

if __name__ == "__main__":
    log.log_progress = True
    testScraper = TheDoctorsKitchenScraper()
    print("Scraping Recipes...")
    recipes = testScraper.n_random_recipes(1)
    print("Inserting recipes into db...")
    insert_recipes(recipes)
    
    for i,r in enumerate(recipes):
        print(f"{i}) {r.title} {r.url}")
    