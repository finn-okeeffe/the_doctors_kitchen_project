def top_ingredients_query(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    extra_meal_str = "OR meal.name IS NULL" if include_unspecified_meal else ""
    extra_diet_str = "OR diet.name IS NULL" if include_unspecified_diet else ""
    query = f"""
    WITH relevant_recipe AS (
        SELECT recipe.id FROM recipe
        LEFT JOIN meal ON meal.recipe_id = recipe.id
        LEFT JOIN diet ON diet.id = recipe.diet_id
        WHERE
            (meal.name IN %s {extra_meal_str}) AND
            (diet.name IN %s {extra_diet_str})
        GROUP BY recipe.id
    )

    SELECT
        ingredient.name,
        COUNT(relevant_recipe.id)
    FROM relevant_recipe
    INNER JOIN ingredient ON relevant_recipe.id = ingredient.recipe_id
    GROUP BY ingredient.name
    ORDER BY COUNT(relevant_recipe.id) DESC
    LIMIT %s;
    """
    return query

def top_equipment_query(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    extra_meal_str = "OR meal.name IS NULL" if include_unspecified_meal else ""
    extra_diet_str = "OR diet.name IS NULL" if include_unspecified_diet else ""
    query = f"""
    WITH relevant_recipe AS (
        SELECT recipe.id FROM recipe
        LEFT JOIN meal ON meal.recipe_id = recipe.id
        LEFT JOIN diet ON diet.id = recipe.diet_id
        WHERE
            (meal.name IN %s {extra_meal_str}) AND
            (diet.name IN %s {extra_diet_str})
        GROUP BY recipe.id
    )

    SELECT
        equipment.name,
        COUNT(relevant_recipe.id)
    FROM relevant_recipe
    INNER JOIN recipe_equipment ON relevant_recipe.id = recipe_equipment.recipe_id
    INNER JOIN equipment ON recipe_equipment.equipment_id = equipment.id
    GROUP BY equipment.name
    ORDER BY COUNT(relevant_recipe.id) DESC
    LIMIT %s;
    """
    return query


def times(include_unspecified_meal: bool, include_unspecified_diet: bool) -> str:
    extra_meal_str = "OR meal.name IS NULL" if include_unspecified_meal else ""
    extra_diet_str = "OR diet.name IS NULL" if include_unspecified_diet else ""
    query = f"""
    SELECT prep_time, cook_time FROM recipe
    LEFT JOIN meal ON meal.recipe_id = recipe.id
    LEFT JOIN diet ON diet.id = recipe.diet_id
    WHERE
        (meal.name IN %s {extra_meal_str}) AND
        (diet.name IN %s {extra_diet_str})
    GROUP BY recipe.id
    LIMIT %s;
    """
    return query