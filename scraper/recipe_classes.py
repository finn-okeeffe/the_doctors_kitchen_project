from bs4 import BeautifulSoup
from typing import List

class Ingredient():
    def __init__(self, name: str, quantity: float, measurement_unit: str=None, preparation: str=None):
        self.name = name
        self.quantity = quantity
        self.measurement_unit = measurement_unit
        self.preparation = preparation
    
    def __repr__(self):
        return f"<Ingredient object: name={self.name.__repr__()}; quantity={self.quantity.__repr__()}, measurement_unit={self.measurement_unit.__repr__()}, preparation={self.preparation.__repr__()}>"
    
    def __str__(self):
        return f"{self.name}, {self.quantity} {self.measurement_unit}, {self.preparation}"

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
        for equipment_name in self.equipment:
            rep += f"- {equipment_name}\n"
        
        rep += self.subheader("ingredients")
        for ingredientObject in self.ingredients:
            rep += f"- {str(ingredientObject)}\n"
        return rep
    
    def subheader(self, string: str) -> str:
        return f"\n## {string.upper()}\n"
    
    def print(self):
        print(self.__str__())