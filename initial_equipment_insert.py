import psycopg2 as pg2
import secret
import pandas as pd

equipment_dict = {
    "pan": {"pan", "frypan"},
    "pot": {"pot", "boil", "saucepan"},
    "blender": {"blend"},
    "air fryer": {"air frier", "air fryer"},
    "toaster": {"toaster", "toast"},
    "oven": {"oven", "bake", "roast"},
    "cast-iron pan": {"cast iron pan"},
    "knife": {"slice", "sliced", "chop", "chopped", "dice", "diced", "cube", "cubed"},
    "chopping board": {"slice", "sliced", "chop", "chopped", "dice", "diced", "cube", "cubed", "board"},
    "measuring spoons": {"tbsp", "tsp"},
    "measuring cup": {"cup", "cups", "ml"},
    "scale": {"g", "gram", "grams"},
    "bowl": {"bowl"},
    "baking paper": {"baking paper", "baking parchment"},
    "fridge": {"fridge", "refridgerator"},
    "freezer": {"freezer", "freeze"},
    "microwave": {"microwave"}
}


conn = pg2.connect(database="the_doctors_kitchen", user=secret.username, password=secret.password)
cur = conn.cursor()

for name, synonyms in equipment_dict.items():
    cur.execute(f"""
                SELECT COUNT(name) FROM equipment WHERE name = '{name}';
                """)
    if cur.fetchone()[0] == 0:
        cur.execute(f"""
                    INSERT INTO equipment(name)
                    VALUES
                        ('{name}');
                    """)
    
    cur.execute(f"SELECT id FROM equipment WHERE name = '{name}'")
    equipment_id = cur.fetchone()[0]

    for phrase in synonyms:
        cur.execute(f"""
                SELECT COUNT(*) FROM equipment_synonym 
                WHERE equipment_id='{equipment_id}' AND synonym='{phrase}';
                """)
        if cur.fetchone()[0] == 0:
            cur.execute(f"""
                        INSERT INTO equipment_synonym(equipment_id, synonym)
                        VALUES
                            ({equipment_id}, '{phrase}');
                        """)
conn.commit()
conn.close()