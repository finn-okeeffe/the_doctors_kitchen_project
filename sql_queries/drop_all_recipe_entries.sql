DELETE FROM ingredient;
ALTER SEQUENCE ingredient_id_seq RESTART WITH 1;
DELETE FROM meal;
ALTER SEQUENCE meal_id_seq RESTART WITH 1;
DELETE FROM recipe_equipment;
ALTER SEQUENCE recipe_equipment_id_seq RESTART WITH 1;
DELETE FROM recipe;
ALTER SEQUENCE recipe_id_seq RESTART WITH 1;