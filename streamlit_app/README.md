# The Streamlit App
---
This folder contains source code for the streamlit app hosted at https://finns-recipe-dashboard.streamlit.app/.
The app queries the recipe database to create visualisations and search recipes for ingredients.
When searching through the recipes, all results link to the recipe page on thedoctorskitchen.com, this app does not aim to replace the original website in any way.

## Visualisations
![A screenshot of the streamlit app, showing a selection box with all options selected, and a chart of the most used ingredients.](https://github.com/finn-okeeffe/the_doctors_kitchen_project/assets/133080250/7177dccc-c8ec-4835-a287-6d633fe1da1f)

This part of the app shows stats about the most used ingredients, the most used equipment, and preparation and cooking time. Select which visualisation to look at through the tabs above the charts.
You can filter recipes by meal (breakfast, lunch, dinner, snack, unspecified), or diet (no diet, pescatarian, vegetarian, vegan) by adding or removing tags in the field above the tags section.

## Searching recipes
![A screenshot of the streamlit app, showing a blank search box and a variety of recipes below.](https://github.com/finn-okeeffe/the_doctors_kitchen_project/assets/133080250/791c6032-d1f6-4473-8450-96d03c2f3d9c)

If you scroll down from the visualisations, you can search through the recipes by ingredient.
Leaving the search box empty displays all results, and entering multiple ingredients separated by commas shows recipes with all of these ingredients.
For example, the following query shows all recipes which use garlic and chilli:
![A screenshot of the streamlit app, showing a search box with the text 'garlic, chilli', and a variety of recipes.](https://github.com/finn-okeeffe/the_doctors_kitchen_project/assets/133080250/923d7d3e-17cf-4959-b4dd-a1ef5c854959)

The search looks for the search terms you give it inside ingredient names. So 'olive' would match both 'olive oil' and 'stuffed olives'.
