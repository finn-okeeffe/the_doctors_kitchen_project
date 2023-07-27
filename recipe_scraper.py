import requests
from bs4 import BeautifulSoup
from equipment_parser import equipment_set
from typing import List, Tuple

class Ingredient():
    def __init__(self, name: str, quantity: float, measurement_unit: str=None, preparation: str=None):
        self.name = name
        self.quantity = quantity
        self.measurement_unit = measurement_unit
        self.preparation = preparation
    
    def __repr__(self):
        return f"<Ingredient object: name={self.name.__repr__()}; quantity={self.quantity.__repr__()}, measurement_unit={self.measurement_unit.__repr__()}, preparation={self.preparation.__repr__()}>"
    
    def __str__(self):
        return f"{self.name}, {self.quantity} {self.preparation}"


class IngredientListFactory():
    def new_ingredient_object_list(self, soup: BeautifulSoup) -> List[Ingredient]:
        itemprop_tag = "recipeIngredient"

        recipeIngredients = soup.find_all(itemprop=itemprop_tag)

        ingredient_objects = []
        for ingredient_soup in recipeIngredients:
            ingredientObject = self.ingredient_soup_to_IngredientObject(ingredient_soup)
            ingredient_objects.append(ingredientObject)
        
        # recipe ingredients are duplicated in the HTML, so we split the list down the middle
        ingredient_objects = ingredient_objects[:len(ingredient_objects)//2]

        return ingredient_objects


    def ingredient_soup_to_IngredientObject(self, ingredient_soup: BeautifulSoup) -> Ingredient:
        metric_measurement_class = "r4-ingre-metric"
        measurement = ingredient_soup.find(class_=metric_measurement_class).text.split()
        preparation_name = "span"
        preparation_class = "block text-md text-gray-400"

        quantity = None
        measurement_unit = None
        if len(measurement) >= 1:
            quantity = float(measurement[0])
        if len(measurement) == 2:
            measurement_unit = measurement[1]
        elif len(measurement) > 2:
            raise ValueError(f"Measurement {measurement} has length {len(measurement)} > 2")
        
        name = ingredient_soup.contents[-2].strip()

        preparation = ingredient_soup.find(preparation_name, preparation_class).text.strip()
        if preparation == "":
            preparation = None
        
        return Ingredient(name, quantity, measurement_unit=measurement_unit, preparation=preparation)


class Recipe():
    def __init__(self,
                 url: str,
                 soup: BeautifulSoup,
                 title: str,
                 description: str,
                 diet: str,
                 meals: List[str],
                 servings: int,
                 prep_time: int,
                 cook_time: int,
                 ingredients: List[Ingredient],
                 equipment: List[str],
                 method: List[str]
                 ):
        
        self.url = url
        self.soup = soup
        self.title = title
        self.description = description
        self.diet = diet
        self.meals = meals
        self.servings = servings
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.ingredients = ingredients
        self.equipment = equipment
        self.method = method
    
    def __str__(self):
        rep = f"# {self.title.upper()}\n"
        rep += f"{self.url}\n"
        rep += f"Total time: {self.prep_time + self.cook_time} mins\n"

        rep += self.subheader("meals")
        for meal in self.meals:
            rep += f"- {meal}\n"

        rep += self.subheader("description")
        rep += f"{self.description}\n"

        rep += self.subheader("equipment")
        for e in self.equipment:
            rep += f"- {e}\n"
        
        rep += self.subheader("ingredients")
        for ingredientObject in self.ingredients:
            rep += f"- {ingredientObject.name}, {ingredientObject.quantity} {ingredientObject.measurement_unit}\n"
        return rep
    
    def subheader(self, string: str) -> str:
        return f"\n## {string.upper()}\n"
    
    def print(self):
        print(self.__str__())
    


class RecipeFactory():
    def new_recipe(self, url: str) -> Recipe:
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
        itemprop_tag = "name"
        return soup.find(itemprop=itemprop_tag).text.strip()
    
    def recipe_servings(self, soup: BeautifulSoup) -> int:
        itemprop_tag = "recipeYield"
        return int(soup.find(itemprop=itemprop_tag).text.strip())
    
    def recipe_diet(self, soup: BeautifulSoup) -> str:
        class_name = "inline-block mr-4 mt-2 xl:text-h3 lg:text-lg text-base text-white print:text-black"
        tag_soup = soup.find(class_=class_name)
        if tag_soup:
            return tag_soup.contents[2].strip()
        else:
            return None
        
    def recipe_meals(self, soup: BeautifulSoup):
        class_name = "inline-block mr-2 mb-2 px-2 py-1.5 md:text-label text-labelsmall font-bold text-white bg-docGreen uppercase tracking-wider"
        name = "a"
        return [subsoup.text.strip() for subsoup in soup.find_all(name, class_=class_name)]
    
    def recipe_prep_time_in_mins(self, soup: BeautifulSoup) -> int:
        prep_time_itemprop_tag = "prepTime"
        prep_time = soup.find(itemprop=prep_time_itemprop_tag).text.strip()
        prep_time = float(prep_time) if len(prep_time)>0 else None
        return prep_time
    
    def recipe_cook_time_in_mins(self, soup: BeautifulSoup) -> int:
        cook_time_itemprop_tag = "cookTime"
        cook_time = soup.find(itemprop=cook_time_itemprop_tag).text.strip()
        cook_time = float(cook_time) if len(cook_time)>0 else None
        return cook_time
    
    def recipe_ingredients_list(self, soup: BeautifulSoup) -> List[Ingredient]:
        ingredientListFactory = IngredientListFactory()
        return ingredientListFactory.new_ingredient_object_list(soup)
    
    def recipe_description(self, soup: BeautifulSoup) -> str:
        itemprop_tag = "description"
        name = "h2"
        desc = soup.find(name, itemprop=itemprop_tag).text.strip()
        desc = None if len(desc) == 0 else desc
        return desc
    
    def recipe_method(self, soup: BeautifulSoup) -> List[str]:
        name = "p"
        itemprop_tag = "description"

        steps_soup_list = soup.find_all(name, itemprop="description")
        steps_list = []
        for step in steps_soup_list:
            for item in step.contents:
                steps_list.append(item.text.strip())
        
        return steps_list
    
    def recipe_equipment_list(self, method: List[str], ingredients_list: List[Ingredient]) -> List[str]:
        ingredients_str_list = [str(ingredient) for ingredient in ingredients_list]
        return equipment_set(method, ingredients_str_list)


if __name__ == "__main__":
    URL = "https://thedoctorskitchen.com/recipes/smoky-mushroom-and-tempeh-veggie-burgers/"
    recipeFactory = RecipeFactory()
    recipeObject = recipeFactory.new_recipe(URL).print()