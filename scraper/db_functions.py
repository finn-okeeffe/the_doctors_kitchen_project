import psycopg2 as pg2
import secret
import log
from recipe_classes import Recipe
import datetime

class DatabaseIdFields():
    diet_ids = {}
    recipe_ids = {}
    equipment_ids = {}

    def __init__(self, cur):
        self.refresh_ids(self,cur)

    def refresh_ids(self, cur):
        self.get_diet_ids(cur)
        self.get_recipe_ids(cur)
        self.get_equipment_ids(cur)

    def get_diet_ids(self, cur):
        cur.execute("SELECT id, name FROM diet;")
        for (diet_id, diet_name) in cur.fetchall():
            self.diet_ids[diet_name] = diet_id

    def get_recipe_ids(self, cur):
        cur.execute("SELECT id, url FROM recipe;")
        for (recipe_id, recipe_url) in cur.fetchall():
            self.recipe_ids[recipe_url] = recipe_id

    def get_equipment_ids(self, cur):
        cur.execute("SELECT id, name FROM equipment;")
        for (equipment_id, equipment_name) in cur.fetchall():
            self.equipment_ids[equipment_name] = equipment_id


class Inserter():
    def __init__(self, cur):
        self.cur: pg2.cursor = cur
        self.ids = DatabaseIdFields(self.cur)

    def add_equipment(self, equipment_name: str):
        if not(equipment_name in self.ids.equipment_ids):
            self.cur.execute(
                """INSERT INTO equipment(name)
                VALUES (%s)""",
                (equipment_name,)
            )
        self.ids.get_equipment_ids()
    
    def add_synonym(self, equipment_name: str, synonym: str):
        self.cur.execute(
            """INSERT INTO equipment_synonym(equipment_id, synonym)
            VALUES (%s, %s)""",
            (self.ids.equipment_ids[equipment_name], synonym)
        )

    def insert_into_recipe_table(self, recipeObject: Recipe):
        diet_id = self.ids.diet_ids[recipeObject.diet]
        self.cur.execute(
            """INSERT INTO recipe(url, title, num_servings, prep_time, cook_time, method, last_update, diet_id, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (recipeObject.url, recipeObject.title, recipeObject.servings,
                recipeObject.prep_time, recipeObject.cook_time,
                " ".join(recipeObject.method),
                str(datetime.datetime.now()), diet_id, recipeObject.description)
        )
        
        # update recipe id dictionary
        self.ids.get_recipe_ids(self.cur)
    
    def insert_into_recipe_equipment_table(self, recipeObject: Recipe):
        recipe_id = self.ids.recipe_ids[recipeObject.url]
        for equipment_name in recipeObject.equipment:
            equipment_id = self.ids.equipment_ids[equipment_name]
            self.cur.execute(
                """INSERT INTO recipe_equipment(recipe_id, equipment_id)
                VALUES (%s, %s);""",
                (recipe_id, equipment_id)
            )
    
    def insert_into_meal_table(self, recipeObject: Recipe):
        recipe_id = self.ids.recipe_ids[recipeObject.url]
        for meal_name in recipeObject.meals:
            self.cur.execute(
                """INSERT INTO meal(recipe_id, name)
                VALUES (%s, %s);""",
                (recipe_id, meal_name)
            )
    
    def insert_into_ingredient_table(self, recipeObject: Recipe):
        recipe_id = self.ids.recipe_ids[recipeObject.url]
        for ingredientObject in recipeObject.ingredients:
            self.cur.execute(
                """INSERT INTO ingredient(recipe_id, name, quantity, unit, preparation)
                VALUES (%s, %s, %s, %s, %s)""",
                (recipe_id, ingredientObject.name, ingredientObject.quantity,
                 ingredientObject.measurement_unit, ingredientObject.preparation)
            )

equipment_dict = {}

def equipment_dict_from_db():
    global eqiupment_dict
    log.log("Connecting to database...")
    conn = pg2.connect(**secret.connection_kw_args)
    cur = conn.cursor()

    log.log("Retrieving equipment ids...")
    cur.execute('SELECT id, name FROM equipment;')
    results = cur.fetchall()
    for (equipment_id,equipment_name) in results:
        # equipment_names[equipment_id] = equipment_name
        cur.execute(f"SELECT synonym FROM equipment_synonym WHERE equipment_id=%s;",(equipment_id,))
        synonyms = {row[0] for row in cur.fetchall()}
        equipment_dict[equipment_name] = synonyms
    
    log.log("Completed, closing database connection")
    conn.close()

def testing_procedure():
    with pg2.connect(**secret.connection_kw_args) as conn:
        with conn.cursor() as cur:
            ids = DatabaseIdFields(cur)
            print(ids.diet_ids)
            print(ids.equipment_ids)
            print(ids.recipe_ids)

if __name__ == "__main__":
    testing_procedure()