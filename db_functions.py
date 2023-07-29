import psycopg2 as pg2
import secret
import log

class DatabaseIdFields():
    diet_ids = {}
    recipe_ids = {}
    equipment_ids = {}

    def __init__(self, cur):
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

def testing_procedure():
    with pg2.connect(database=secret.database_name, user=secret.username, password=secret.password) as conn:
        with conn.cursor() as cur:
            ids = DatabaseIdFields(cur)
            print(ids.diet_ids)
            print(ids.equipment_ids)
            print(ids.recipe_ids)

if __name__ == "__main__":
    testing_procedure()