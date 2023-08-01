def top_ingredients_query(include_unspecified_meal: bool, include_unspecified_diet: bool):
    extra_meal_str = "OR meal.name IS NULL" if include_unspecified_meal else ""
    extra_diet_str = "OR diet.name IS NULL" if include_unspecified_diet else ""
    query = f"""
    WITH relevant_meals AS (
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
        COUNT(relevant_meals.id)
    FROM relevant_meals
    INNER JOIN ingredient ON relevant_meals.id = ingredient.recipe_id
    GROUP BY ingredient.name
    ORDER BY COUNT(relevant_meals.id) DESC
    LIMIT %s;
    """
    return query