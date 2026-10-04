import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.user import User
from models.pantry import PantryItem
from models.recipe import Recipe, RecipeIngredient
from models.waste import FoodWaste
from datetime import date, timedelta

def seed_recipes(app):
    with app.app_context():
        # Clear existing recipes
        RecipeIngredient.query.delete()
        Recipe.query.delete()
        db.session.commit()
        
        recipes_data = [
            # Indian Recipes
            {
                'name': 'Vegetable Pulao',
                'description': 'A fragrant and delicious rice dish made with mixed vegetables and spices.',
                'instructions': '1. Wash rice and soak for 30 minutes.\n2. Sauté onions, ginger, and garlic in ghee.\n3. Add chopped vegetables and spices. Cook for 5 minutes.\n4. Add soaked rice and water.\n5. Cook until rice is tender and water is absorbed.',
                'cooking_time': 30,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('rice', '1', 'cup'), ('onion', '1', 'piece'), ('carrot', '1', 'piece'), ('potato', '1', 'piece')]
            },
            {
                'name': 'Paneer Bhurji',
                'description': 'A quick and easy scrambled cottage cheese dish flavoured with Indian spices.',
                'instructions': '1. Heat oil in a pan and add cumin seeds.\n2. Add chopped onions and sauté until golden.\n3. Add tomatoes, green chilies, and spices.\n4. Crumble the paneer and add to the pan.\n5. Mix well and cook for 3-4 minutes. Garnish with coriander.',
                'cooking_time': 20,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('paneer', '200', 'g'), ('onion', '1', 'piece'), ('tomato', '1', 'piece')]
            },
            {
                'name': 'Aloo Paratha',
                'description': 'A popular Indian whole wheat flatbread stuffed with a spiced potato mixture.',
                'instructions': '1. Boil and mash the potatoes.\n2. Mix mashed potatoes with spices and finely chopped onions.\n3. Knead wheat flour into a soft dough.\n4. Roll out a small portion of dough, place the potato filling in the center, and seal the edges.\n5. Roll out gently and cook on a hot griddle with butter or oil until golden brown on both sides.',
                'cooking_time': 40,
                'difficulty': 'Medium',
                'dietary_type': 'Vegetarian',
                'ingredients': [('potato', '2', 'pieces'), ('onion', '1', 'piece')]
            },
            {
                'name': 'Poha',
                'description': 'A light and healthy breakfast made with flattened rice, peanuts, and spices.',
                'instructions': '1. Rinse the poha in water and drain well.\n2. Heat oil, add mustard seeds, curry leaves, and green chilies.\n3. Add chopped onions and sauté until translucent.\n4. Add turmeric powder and the drained poha.\n5. Mix well, cook for 2 minutes, and garnish with coriander and lemon juice.',
                'cooking_time': 15,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('onion', '1', 'piece'), ('potato', '1', 'piece')]
            },
            {
                'name': 'Upma',
                'description': 'A traditional South Indian breakfast dish made from dry roasted semolina.',
                'instructions': '1. Dry roast the semolina until slightly aromatic.\n2. In a pan, heat oil and add mustard seeds, urad dal, and curry leaves.\n3. Add chopped onions and sauté.\n4. Add water and salt, and bring to a boil.\n5. Slowly add the roasted semolina while stirring continuously to avoid lumps. Cook until thick.',
                'cooking_time': 20,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('onion', '1', 'piece'), ('carrot', '1', 'piece')]
            },
            {
                'name': 'Masala Omelette',
                'description': 'A spicy and flavourful Indian style egg omelette.',
                'instructions': '1. Crack eggs into a bowl and whisk well.\n2. Add finely chopped onions, tomatoes, green chilies, and coriander.\n3. Add salt, turmeric, and chili powder to taste.\n4. Heat oil or butter in a pan.\n5. Pour the egg mixture and cook until golden on both sides.',
                'cooking_time': 10,
                'difficulty': 'Easy',
                'dietary_type': 'Non-Vegetarian',
                'ingredients': [('egg', '2', 'pieces'), ('onion', '1', 'piece'), ('tomato', '1', 'piece')]
            },
            {
                'name': 'Tomato Rice',
                'description': 'A tangy and spicy South Indian rice dish made with tomatoes and spices.',
                'instructions': '1. Heat oil in a pan, add mustard seeds and curry leaves.\n2. Add sliced onions and sauté until golden.\n3. Add chopped tomatoes, turmeric, and chili powder. Cook until tomatoes are soft and mushy.\n4. Add cooked rice and mix gently.\n5. Garnish with fresh coriander leaves.',
                'cooking_time': 25,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('rice', '1', 'cup'), ('tomato', '3', 'pieces'), ('onion', '1', 'piece')]
            },
            {
                'name': 'Dal Khichdi',
                'description': 'A comforting and wholesome one-pot meal made with rice and lentils.',
                'instructions': '1. Wash and soak rice and lentils (dal) together for 30 minutes.\n2. Heat ghee in a pressure cooker, add cumin seeds and a pinch of asafoetida.\n3. Add chopped onions and sauté.\n4. Add tomatoes, turmeric, and salt. Mix well.\n5. Add the soaked rice and dal with water, and pressure cook for 3 whistles.',
                'cooking_time': 35,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('rice', '1', 'cup'), ('dal/lentils', '1/2', 'cup'), ('onion', '1', 'piece'), ('tomato', '1', 'piece')]
            },
            {
                'name': 'Mixed Vegetable Curry',
                'description': 'A vibrant and healthy curry loaded with seasonal vegetables.',
                'instructions': '1. Chop all vegetables (carrots, potatoes, capsicum, etc.) into bite-sized pieces.\n2. Heat oil, sauté onions and ginger-garlic paste until aromatic.\n3. Add tomatoes and dry spice powders. Cook until oil separates.\n4. Add the chopped vegetables and a little water.\n5. Cover and simmer until the vegetables are tender.',
                'cooking_time': 35,
                'difficulty': 'Medium',
                'dietary_type': 'Vegetarian',
                'ingredients': [('carrot', '1', 'piece'), ('potato', '1', 'piece'), ('capsicum/bell pepper', '1', 'piece'), ('onion', '1', 'piece'), ('tomato', '1', 'piece')]
            },
            {
                'name': 'Egg Bhurji',
                'description': 'Spicy scrambled eggs, a popular Indian street food.',
                'instructions': '1. Heat oil in a pan and add cumin seeds.\n2. Sauté chopped onions, green chilies, and ginger until onions are translucent.\n3. Add chopped tomatoes, turmeric, and red chili powder. Cook until tomatoes soften.\n4. Crack eggs directly into the pan and stir continuously.\n5. Cook until the eggs are scrambled and fully set. Garnish with coriander.',
                'cooking_time': 15,
                'difficulty': 'Easy',
                'dietary_type': 'Non-Vegetarian',
                'ingredients': [('egg', '3', 'pieces'), ('onion', '1', 'piece'), ('tomato', '1', 'piece')]
            },
            {
                'name': 'Vegetable Fried Rice',
                'description': 'Indo-Chinese style fried rice with crunchy vegetables.',
                'instructions': '1. Cook rice and let it cool completely.\n2. Finely chop carrots, capsicum, and onions.\n3. Heat oil in a wok or large pan over high heat.\n4. Stir-fry the vegetables quickly to retain their crunch.\n5. Add the cooled rice, soy sauce, salt, and pepper. Toss well and serve hot.',
                'cooking_time': 25,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('rice', '1', 'cup'), ('carrot', '1', 'piece'), ('capsicum/bell pepper', '1', 'piece'), ('onion', '1', 'piece')]
            },
            {
                'name': 'Tomato Soup',
                'description': 'A classic, comforting homemade tomato soup.',
                'instructions': '1. Roughly chop tomatoes and onions.\n2. Boil them together with a little water and a clove of garlic until soft.\n3. Let the mixture cool, then blend into a smooth puree.\n4. Strain the puree into a pot to remove seeds and skin.\n5. Simmer the soup, adding salt, pepper, and a pinch of sugar. Serve with croutons.',
                'cooking_time': 20,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('tomato', '4', 'pieces'), ('onion', '1', 'piece'), ('bread', '2', 'pieces')]
            },
            {
                'name': 'Aloo Sabzi',
                'description': 'A simple and flavourful dry potato stir-fry.',
                'instructions': '1. Peel and cube potatoes.\n2. Heat oil in a pan, add mustard and cumin seeds.\n3. Add a pinch of turmeric and the cubed potatoes.\n4. Sauté for a few minutes, then cover and cook until potatoes are tender.\n5. Sprinkle red chili powder and coriander powder. Mix well and serve.',
                'cooking_time': 20,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('potato', '3', 'pieces')]
            },
            {
                'name': 'Paneer Sandwich',
                'description': 'A quick and filling sandwich with a spiced paneer filling.',
                'instructions': '1. Crumble paneer and mix with finely chopped onions, salt, and pepper.\n2. Take two slices of bread and butter one side of each.\n3. Place the paneer mixture between the slices (butter side out).\n4. Toast in a sandwich maker or on a pan until golden and crispy.\n5. Slice diagonally and serve with ketchup.',
                'cooking_time': 15,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('bread', '2', 'pieces'), ('paneer', '50', 'g'), ('onion', '1/2', 'piece')]
            },
            {
                'name': 'Banana Smoothie',
                'description': 'A healthy, thick, and creamy banana milkshake.',
                'instructions': '1. Peel and slice the bananas.\n2. Add bananas, chilled milk, and a little honey or sugar to a blender.\n3. Blend until smooth and frothy.\n4. Pour into a glass.\n5. Serve immediately, optionally garnished with a pinch of cinnamon.',
                'cooking_time': 5,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('banana', '2', 'pieces'), ('milk', '1', 'cup')]
            },
            {
                'name': 'Bread Upma',
                'description': 'A quick South Indian style snack made using leftover bread.',
                'instructions': '1. Cut bread slices into small cubes.\n2. Heat oil in a pan, add mustard seeds and curry leaves.\n3. Add chopped onions and green chilies. Sauté until onions soften.\n4. Add chopped tomatoes, turmeric, and salt. Cook until tomatoes are mushy.\n5. Toss in the bread cubes and mix gently until coated with the masala.',
                'cooking_time': 15,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('bread', '4', 'pieces'), ('onion', '1', 'piece'), ('tomato', '1', 'piece')]
            },
            {
                'name': 'Egg Curry',
                'description': 'Hard-boiled eggs simmered in a flavourful onion-tomato gravy.',
                'instructions': '1. Hard boil the eggs, peel, and make small slits on them.\n2. Heat oil, sauté finely chopped onions until golden brown.\n3. Add ginger-garlic paste, then chopped tomatoes and spices (coriander, cumin, garam masala).\n4. Cook until the oil separates from the masala, then add water to form a gravy.\n5. Gently add the boiled eggs, cover, and simmer for 5 minutes.',
                'cooking_time': 30,
                'difficulty': 'Medium',
                'dietary_type': 'Non-Vegetarian',
                'ingredients': [('egg', '4', 'pieces'), ('onion', '2', 'pieces'), ('tomato', '2', 'pieces')]
            },
            {
                'name': 'Aloo Gobi',
                'description': 'A classic Indian dry curry made with potatoes and cauliflower.',
                'instructions': '1. Cut potatoes into cubes and cauliflower into florets.\n2. Heat oil in a pan, add cumin seeds.\n3. Add chopped onions and sauté until translucent.\n4. Add tomatoes, turmeric, coriander powder, and the chopped vegetables.\n5. Cover and cook on low heat until the vegetables are tender, stirring occasionally.',
                'cooking_time': 30,
                'difficulty': 'Medium',
                'dietary_type': 'Vegetarian',
                'ingredients': [('potato', '2', 'pieces'), ('onion', '1', 'piece'), ('tomato', '1', 'piece')]
            },
            
            # International Recipes
            {
                'name': 'Pasta Aglio e Olio',
                'description': 'A traditional Italian pasta dish featuring garlic and olive oil.',
                'instructions': '1. Boil pasta in salted water until al dente.\n2. Thinly slice garlic cloves.\n3. Heat olive oil in a pan over low heat and gently sauté the garlic until golden.\n4. Add red pepper flakes for heat.\n5. Toss the cooked pasta in the garlic oil, add a splash of pasta water, and garnish with parsley.',
                'cooking_time': 20,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('pasta', '200', 'g')]
            },
            {
                'name': 'Vegetable Pasta',
                'description': 'A quick and easy pasta dish tossed with mixed vegetables in a tomato base.',
                'instructions': '1. Boil pasta according to package instructions.\n2. Chop capsicum, onions, and carrots.\n3. Sauté onions and garlic in a pan, then add the chopped vegetables.\n4. Stir in tomato puree, herbs, and salt, cooking until slightly thickened.\n5. Mix the boiled pasta into the sauce and serve hot.',
                'cooking_time': 25,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('pasta', '200', 'g'), ('onion', '1', 'piece'), ('capsicum/bell pepper', '1', 'piece'), ('carrot', '1', 'piece'), ('tomato', '2', 'pieces')]
            },
            {
                'name': 'Grilled Cheese Sandwich',
                'description': 'The ultimate comfort food: melted cheese between toasted bread slices.',
                'instructions': '1. Butter one side of two slices of bread.\n2. Place one slice, butter-side down, in a skillet over medium-low heat.\n3. Top with slices of cheese.\n4. Place the second slice of bread on top, butter-side up.\n5. Cook until the bottom is golden brown, then flip and cook until the cheese is melted and the other side is golden.',
                'cooking_time': 10,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('bread', '2', 'pieces'), ('cheese', '2', 'slices')]
            },
            {
                'name': 'Classic Omelette',
                'description': 'A simple, light, and fluffy French-style omelette.',
                'instructions': '1. Whisk eggs in a bowl until whites and yolks are fully combined.\n2. Melt butter in a non-stick skillet over medium heat.\n3. Pour in the eggs and gently pull cooked edges to the center, letting uncooked egg flow underneath.\n4. Season with salt and pepper.\n5. Once set but still slightly soft on top, fold in half and slide onto a plate.',
                'cooking_time': 10,
                'difficulty': 'Easy',
                'dietary_type': 'Non-Vegetarian',
                'ingredients': [('egg', '3', 'pieces')]
            },
            {
                'name': 'Tomato Toast',
                'description': 'A quick and refreshing snack of fresh tomatoes on crispy toast.',
                'instructions': '1. Toast slices of bread until golden and crisp.\n2. Slice fresh tomatoes thinly.\n3. Drizzle a little olive oil over the toast.\n4. Arrange the tomato slices on top.\n5. Sprinkle with salt, pepper, and a little oregano or fresh basil.',
                'cooking_time': 5,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('bread', '2', 'pieces'), ('tomato', '1', 'piece')]
            },
            {
                'name': 'Vegetable Wrap',
                'description': 'A quick, healthy wrap filled with crunchy fresh vegetables.',
                'instructions': '1. Lay a tortilla or large flatbread on a clean surface.\n2. Spread a layer of cream cheese, hummus, or mayonnaise in the center.\n3. Layer thinly sliced cucumbers, carrots, onions, and lettuce.\n4. Season with salt and pepper.\n5. Fold the sides inward and roll tightly from the bottom up.',
                'cooking_time': 10,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('bread', '1', 'large'), ('carrot', '1', 'piece'), ('onion', '1/2', 'piece')]
            },
            {
                'name': 'Potato Soup',
                'description': 'A rich, creamy, and comforting potato soup.',
                'instructions': '1. Peel and dice potatoes and chop onions.\n2. In a large pot, sauté onions in butter until soft.\n3. Add potatoes and chicken or vegetable broth, bringing to a boil.\n4. Reduce heat, cover, and simmer until potatoes are very tender (about 15 mins).\n5. Blend the soup slightly, stir in milk or cream, and heat gently without boiling.',
                'cooking_time': 30,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('potato', '4', 'pieces'), ('onion', '1', 'piece'), ('milk', '1', 'cup')]
            },
            {
                'name': 'Egg Sandwich',
                'description': 'A classic egg salad sandwich, perfect for lunch.',
                'instructions': '1. Hard boil the eggs, peel them, and chop them into small pieces.\n2. In a bowl, mix the chopped eggs with mayonnaise, a little mustard, salt, and pepper.\n3. Toast the bread slices if desired.\n4. Spoon the egg mixture onto one slice of bread.\n5. Top with lettuce and the other slice of bread. Cut in half to serve.',
                'cooking_time': 10,
                'difficulty': 'Easy',
                'dietary_type': 'Non-Vegetarian',
                'ingredients': [('egg', '2', 'pieces'), ('bread', '2', 'pieces')]
            },
            {
                'name': 'French Toast',
                'description': 'Sweet, pan-fried bread soaked in a cinnamon egg mixture.',
                'instructions': '1. In a shallow dish, whisk together eggs, milk, cinnamon, and a pinch of salt.\n2. Heat a pan over medium heat and melt a little butter.\n3. Dip bread slices into the egg mixture, coating both sides evenly.\n4. Place the bread in the pan and cook until golden brown on the bottom.\n5. Flip and cook the other side. Serve with syrup or fruit.',
                'cooking_time': 15,
                'difficulty': 'Easy',
                'dietary_type': 'Non-Vegetarian',
                'ingredients': [('bread', '4', 'pieces'), ('egg', '2', 'pieces'), ('milk', '1/2', 'cup')]
            },
            {
                'name': 'Fried Rice',
                'description': 'A quick and versatile classic fried rice made with eggs and veggies.',
                'instructions': '1. Ensure you have cold, cooked rice ready.\n2. Heat oil in a wok or large skillet. Scramble the eggs and remove them to a plate.\n3. In the same pan, sauté diced carrots, onions, and peas until tender.\n4. Add the cold rice and soy sauce, tossing constantly over high heat.\n5. Return the scrambled eggs to the pan, mix well, and serve hot.',
                'cooking_time': 20,
                'difficulty': 'Easy',
                'dietary_type': 'Non-Vegetarian',
                'ingredients': [('rice', '2', 'cups'), ('egg', '2', 'pieces'), ('onion', '1', 'piece'), ('carrot', '1', 'piece')]
            },
            {
                'name': 'Vegetable Stir Fry',
                'description': 'A fast and healthy mix of vegetables quickly sautéed with soy sauce.',
                'instructions': '1. Slice carrots, capsicum, and onions into uniform strips.\n2. Heat oil in a wok or large pan over medium-high heat.\n3. Add the vegetables and stir-fry briskly for 3-5 minutes until they are tender-crisp.\n4. Mix soy sauce, a little sugar, and a splash of vinegar in a small bowl, then pour over the veggies.\n5. Toss to coat evenly and serve immediately, alone or over rice.',
                'cooking_time': 15,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('carrot', '2', 'pieces'), ('capsicum/bell pepper', '1', 'piece'), ('onion', '1', 'piece')]
            },
            {
                'name': 'Banana Pancakes',
                'description': 'Fluffy, sweet pancakes naturally flavored with mashed bananas.',
                'instructions': '1. In a bowl, mash the bananas until very smooth.\n2. Whisk in eggs, milk, and a little melted butter.\n3. Stir in flour, baking powder, and a pinch of salt until just combined (don\'t overmix).\n4. Heat a lightly oiled griddle or pan over medium-high heat.\n5. Pour batter onto the griddle, cook until bubbles form, then flip and cook until golden.',
                'cooking_time': 20,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('banana', '2', 'pieces'), ('egg', '1', 'piece'), ('milk', '1/2', 'cup')]
            },
            {
                'name': 'Cheese Omelette',
                'description': 'A gooey, cheese-stuffed omelette perfect for breakfast.',
                'instructions': '1. Crack eggs into a bowl, add a splash of milk, salt, and pepper, and whisk well.\n2. Grate your favorite cheese.\n3. Melt butter in a non-stick skillet over medium heat and pour in the eggs.\n4. As the eggs set, sprinkle the grated cheese over one half.\n5. Fold the other half over the cheese, cook for 30 more seconds, and slide onto a plate.',
                'cooking_time': 10,
                'difficulty': 'Easy',
                'dietary_type': 'Non-Vegetarian',
                'ingredients': [('egg', '3', 'pieces'), ('cheese', '50', 'g'), ('milk', '2', 'tbsp')]
            },
            {
                'name': 'Garlic Bread',
                'description': 'Warm, buttery, and garlicky toasted bread.',
                'instructions': '1. Preheat oven or a heavy skillet.\n2. Mince garlic finely and mix it thoroughly with softened butter and chopped parsley.\n3. Slice bread or a baguette into thick pieces.\n4. Spread the garlic butter generously on one side of each slice.\n5. Bake or toast on a pan until the edges are crispy and butter is melted.',
                'cooking_time': 10,
                'difficulty': 'Easy',
                'dietary_type': 'Vegetarian',
                'ingredients': [('bread', '4', 'slices')]
            }
        ]
        
        for r in recipes_data:
            recipe = Recipe(
                name=r['name'],
                description=r['description'],
                instructions=r['instructions'],
                cooking_time=r['cooking_time'],
                difficulty=r['difficulty'],
                dietary_type=r['dietary_type']
            )
            db.session.add(recipe)
            db.session.flush()
            for ing in r['ingredients']:
                ri = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_name=ing[0],
                    quantity=ing[1],
                    unit=ing[2]
                )
                db.session.add(ri)
        db.session.commit()
        print(f'Seeded {len(recipes_data)} recipes')

def seed_demo_user(app):
    with app.app_context():
        # Create demo user if not exists
        user = User.query.filter_by(email='demo@smartpantry.local').first()
        if not user:
            user = User(name='Demo User', email='demo@smartpantry.local')
            user.set_password('Demo@123')
            db.session.add(user)
            db.session.commit()
        
        # Add demo pantry items
        PantryItem.query.filter_by(user_id=user.id).delete()
        today = date.today()
        
        items = [
            {'name': 'Milk', 'category': 'Dairy', 'quantity': 1.0, 'unit': 'litre', 'purchase_date': today, 'expiry_date': today + timedelta(days=1)},
            {'name': 'Bread', 'category': 'Bakery', 'quantity': 6.0, 'unit': 'pieces', 'purchase_date': today, 'expiry_date': today + timedelta(days=2)},
            {'name': 'Tomato', 'category': 'Vegetables', 'quantity': 4.0, 'unit': 'pieces', 'purchase_date': today, 'expiry_date': today + timedelta(days=3)},
            {'name': 'Paneer', 'category': 'Dairy', 'quantity': 200.0, 'unit': 'g', 'purchase_date': today, 'expiry_date': today + timedelta(days=4)},
            {'name': 'Eggs', 'category': 'Other', 'quantity': 6.0, 'unit': 'pieces', 'purchase_date': today, 'expiry_date': today + timedelta(days=10)},
            {'name': 'Rice', 'category': 'Grains', 'quantity': 1.0, 'unit': 'kg', 'purchase_date': today, 'expiry_date': today + timedelta(days=60)},
            {'name': 'Onion', 'category': 'Vegetables', 'quantity': 5.0, 'unit': 'pieces', 'purchase_date': today, 'expiry_date': today + timedelta(days=14)},
            {'name': 'Cheese', 'category': 'Dairy', 'quantity': 100.0, 'unit': 'g', 'purchase_date': today, 'expiry_date': today + timedelta(days=3)},
            {'name': 'Banana', 'category': 'Fruits', 'quantity': 4.0, 'unit': 'pieces', 'purchase_date': today, 'expiry_date': today + timedelta(days=2)},
            {'name': 'Potato', 'category': 'Vegetables', 'quantity': 6.0, 'unit': 'pieces', 'purchase_date': today, 'expiry_date': today + timedelta(days=20)},
            {'name': 'Pasta', 'category': 'Grains', 'quantity': 200.0, 'unit': 'g', 'purchase_date': today, 'expiry_date': today + timedelta(days=90)},
            {'name': 'Carrot', 'category': 'Vegetables', 'quantity': 3.0, 'unit': 'pieces', 'purchase_date': today, 'expiry_date': today + timedelta(days=7)},
            {'name': 'Capsicum', 'category': 'Vegetables', 'quantity': 2.0, 'unit': 'pieces', 'purchase_date': today, 'expiry_date': today + timedelta(days=5)},
            {'name': 'Dal', 'category': 'Grains', 'quantity': 500.0, 'unit': 'g', 'purchase_date': today, 'expiry_date': today + timedelta(days=30)},
        ]
        
        for item in items:
            db.session.add(PantryItem(**item, user_id=user.id))
        db.session.commit()
        print('Demo user and pantry seeded')

if __name__ == '__main__':
    app = create_app()
    seed_recipes(app)
    seed_demo_user(app)
    print('Seeding complete!')
    print('Demo credentials: demo@smartpantry.local / Demo@123')
