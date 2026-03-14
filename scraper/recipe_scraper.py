# Classes and functions to scrape a single recipe from The Doctors Kitchen
# Finn O'Keeffe - 28/07/2023

import requests
from bs4 import BeautifulSoup
from equipment_parser import equipment_set, load_equipment_dict
from typing import List, Tuple
import log
from re import search
import re
from recipe_classes import Ingredient, Recipe
import argparse


class IngredientListFactory():
    def new_ingredient_object_list(self, soup: BeautifulSoup) -> List[Ingredient]:
        recipeIngredients = soup.find_all(attrs={"data-ingredient-id":True})

        ingredient_objects = []
        for ingredient_soup in recipeIngredients:
            ingredientObject = self.ingredient_soup_to_IngredientObject(ingredient_soup)
            ingredient_objects.append(ingredientObject)
        
        # recipe ingredients are duplicated in the HTML, so we split the list down the middle
        ingredient_objects = ingredient_objects[:len(ingredient_objects)//2]

        return ingredient_objects


    def ingredient_soup_to_IngredientObject(self, ingredient_soup: BeautifulSoup) -> Ingredient:
        quantity = None
        measurement_unit = None
        name = ingredient_soup.contents[3].contents[1].text.strip()

        preparation = ingredient_soup.contents[3].contents[3].text.strip()
        if preparation == "":
            preparation = None
        
        return Ingredient(name, quantity, measurement_unit=measurement_unit, preparation=preparation)



    


class RecipeFactory():
    def __init__(self):
        load_equipment_dict()
        self.ingredientListFactory = IngredientListFactory()

    def new_recipe(self, url: str) -> Recipe:
        log.log(f"scraping url {url} ...")
        soup, code = self.get_soup(url)
        if code != 200:
            raise Exception(f"Request to url {url} raised unexpected code {code}")
        
        method = self.recipe_method(soup)
        ingredients_list = self.recipe_ingredients_list(soup)
        
        
        return Recipe(
            url,
            soup,
            self.recipe_title(soup),
            self.recipe_description(soup),
            self.recipe_diet(soup),
            self.recipe_meals(soup),
            self.recipe_servings(soup),
            self.recipe_prep_time_in_mins(soup),
            self.recipe_cook_time_in_mins(soup),
            ingredients_list,
            self.recipe_equipment_list(method, ingredients_list),
            method
        )

    def get_soup(self, url: str) -> Tuple[BeautifulSoup, int]:
        page = requests.get(url)

        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            return soup, page.status_code
        else:
            return None, page.status_code
    
    def recipe_title(self, soup: BeautifulSoup) -> str:
        return soup.find("h1").text.strip()
    
    def recipe_servings(self, soup: BeautifulSoup) -> int:
        parent_div_id = "ingredients-controls-container"
        servings_class = "mx-2"
        servings_property="data-recipe-portions"
        return int(soup.find("div",id=parent_div_id).find("span", class_=servings_class).get(servings_property))
    
    def recipe_diet(self, soup: BeautifulSoup) -> str:
        class_name = "inline-block mr-4 mt-2 xl:text-h3 lg:text-lg text-base text-white print:text-black"
        tag_soup = soup.find(class_=class_name)
        if tag_soup:
            diet = tag_soup.contents[2].strip()
            if diet == "":
                diet = "None"
            return diet
        else:
            return "None"
        
    def recipe_meals(self, soup: BeautifulSoup):
        class_name = "inline-block mr-2 mb-2 px-2 py-1.5 md:text-label text-labelsmall font-bold text-white bg-docGreen uppercase tracking-wider"
        name = "a"
        return [subsoup.text.strip() for subsoup in soup.find_all(name, class_=class_name)]
    
    def recipe_prep_time_in_mins(self, soup: BeautifulSoup) -> int | None:
        prep_time_span=soup.find_all("span", class_="fs-4")

        if not prep_time_span:
            return None

        prep_time_text = prep_time_span[0].text.strip()
        prep_time = float(re.search(r'(\d+)', prep_time_text).group(1))
        return prep_time
    
    def recipe_cook_time_in_mins(self, soup: BeautifulSoup) -> int|None:
        cook_time_span=soup.find_all("span", class_="fs-4")

        if not cook_time_span:
            return None

        cook_time_text = cook_time_span[1].text.strip()
        cook_time = float(re.search(r'(\d+)', cook_time_text).group(1))
        return cook_time
    
    def recipe_ingredients_list(self, soup: BeautifulSoup) -> List[Ingredient]:
        return self.ingredientListFactory.new_ingredient_object_list(soup)
    
    def recipe_description(self, soup: BeautifulSoup) -> str:
        tag = "p"
        class_ = "mb-sm-3 mb-2 grey lh-md recipe-description-intro-only"
        desc = soup.find(tag, class_=class_).find("span",class_="d-none d-md-inline").text.strip()
        desc = None if len(desc) == 0 else desc
        return desc
    
    def recipe_method(self, soup: BeautifulSoup) -> List[str]:
        step_num = 1
        steps_list = []
        while step_num < 100:
            step_div=soup.find(id=f"instruction_step_{step_num}")
            if step_div is None:
                break
            steps_list.append(step_div.find("p").text.strip())
            step_num += 1
        else:
            log.log(f"[WARNING] Reached max step number for URL {soup.url}")
        
        return steps_list
    
    def recipe_equipment_list(self, method: List[str], ingredients_list: List[Ingredient]) -> List[str]:
        ingredients_str_list = [str(ingredient) for ingredient in ingredients_list]
        return equipment_set(method, ingredients_str_list)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    DEFAULT_URL = "https://thedoctorskitchen.com/recipes/smoky-mushroom-and-tempeh-veggie-burgers/"
    argument_parser.add_argument("url", default=DEFAULT_URL)
    args = argument_parser.parse_args()
    log.logging = True
    recipeFactory = RecipeFactory()
    recipeObject = recipeFactory.new_recipe(args.url).print()
