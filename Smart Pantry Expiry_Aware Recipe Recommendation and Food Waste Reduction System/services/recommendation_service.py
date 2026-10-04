from models.recipe import Recipe
from models.pantry import PantryItem
from extensions import db
from datetime import date

def calculate_match(recipe, pantry_items):
    matched_ingredients = []
    expiring_matches = []
    
    total_recipe_ingredients = len(recipe.ingredients)
    if total_recipe_ingredients == 0:
        return {
            'match_count': 0, 'total': 0, 'match_pct': 0, 
            'expiry_score': 0, 'final_score': 0, 
            'matched_items': [], 'expiring_matches': []
        }
        
    for rec_ing in recipe.ingredients:
        best_match = None
        for p_item in pantry_items:
            if rec_ing.ingredient_name.lower() in p_item.name.lower() or p_item.name.lower() in rec_ing.ingredient_name.lower():
                best_match = p_item
                break
                
        if best_match:
            matched_ingredients.append(best_match)
            if best_match.computed_status in ['Expired', 'Expires Today', 'Expiring Soon']:
                expiring_matches.append(best_match)
                
    match_count = len(matched_ingredients)
    match_pct = match_count / total_recipe_ingredients
    
    expiry_priority_sum = 0
    for item in matched_ingredients:
        days = item.days_remaining
        if days <= 0:
            expiry_priority_sum += 1.0
        elif 1 <= days <= 3:
            expiry_priority_sum += 0.85
        elif 4 <= days <= 7:
            expiry_priority_sum += 0.60
        else:
            expiry_priority_sum += 0.20
            
    expiry_priority = expiry_priority_sum / total_recipe_ingredients if total_recipe_ingredients else 0
    
    availability = 1.0 if match_pct >= 0.5 else match_pct * 2
    
    final_score = (match_pct * 0.60) + (expiry_priority * 0.30) + (availability * 0.10)
    final_score_normalized = min(100, max(0, round(final_score * 100)))
    
    return {
        'match_count': match_count,
        'total': total_recipe_ingredients,
        'match_pct': match_pct,
        'expiry_score': expiry_priority,
        'final_score': final_score_normalized,
        'matched_items': matched_ingredients,
        'expiring_matches': expiring_matches
    }

def get_recommendations(user_id, limit=6):
    pantry_items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    recipes = Recipe.query.all()
    
    recommendations = []
    for recipe in recipes:
        match_info = calculate_match(recipe, pantry_items)
        if match_info['match_count'] > 0:
            recommendations.append({
                'recipe': recipe,
                'match_info': match_info
            })
            
    recommendations.sort(key=lambda x: x['match_info']['final_score'], reverse=True)
    return recommendations[:limit]

def get_recipe_ingredient_status(recipe_id, user_id):
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe: return []
    
    pantry_items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    
    result = []
    for ing in recipe.ingredients:
        matched = False
        for p_item in pantry_items:
            if ing.ingredient_name.lower() in p_item.name.lower() or p_item.name.lower() in ing.ingredient_name.lower():
                status_label = 'available'
                if p_item.computed_status in ['Expiring Soon', 'Expires Today', 'Expired']:
                    status_label = 'expiring'
                result.append({
                    'ingredient_name': ing.ingredient_name,
                    'quantity': ing.quantity,
                    'unit': ing.unit,
                    'status': status_label,
                    'days_remaining': p_item.days_remaining,
                    'pantry_item': p_item
                })
                matched = True
                break
        if not matched:
            result.append({
                'ingredient_name': ing.ingredient_name,
                'quantity': ing.quantity,
                'unit': ing.unit,
                'status': 'missing',
                'days_remaining': None,
                'pantry_item': None
            })
    return result
