from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.recipe import Recipe
from models.pantry import PantryItem
from extensions import db
from utils import login_required
from services.recommendation_service import get_recommendations, get_recipe_ingredient_status, calculate_match

recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')


def _get_notifications(user_id):
    from services.expiry_service import get_pantry_summary
    summary = get_pantry_summary(user_id)
    return {
        'expiring_count': summary.get('expiring_soon_count', 0),
        'expired_count': summary.get('expired_count', 0),
    }


@recipes_bp.route('')
@recipes_bp.route('/')
@login_required
def list_recipes():
    user_id = session['user_id']
    search = request.args.get('q', '').strip()
    diet = request.args.get('diet', '').strip()
    difficulty = request.args.get('difficulty', '').strip()

    # Get all recipes scored against pantry
    pantry_items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    all_recipes = Recipe.query.all()

    scored = []
    for recipe in all_recipes:
        match_info = calculate_match(recipe, pantry_items)
        scored.append({
            'recipe': recipe,
            'match_info': match_info
        })

    # Apply filters
    if search:
        search_lower = search.lower()
        scored = [r for r in scored if search_lower in r['recipe'].name.lower()
                  or search_lower in r['recipe'].description.lower()]
    if diet:
        scored = [r for r in scored if r['recipe'].dietary_type == diet]
    if difficulty:
        scored = [r for r in scored if r['recipe'].difficulty == difficulty]

    # Sort by final score descending, then by name
    scored.sort(key=lambda x: (-x['match_info']['final_score'], x['recipe'].name))

    notifications = _get_notifications(user_id)

    return render_template('recipes.html',
                           recipes=scored,
                           search_query=search,
                           filter_dietary=diet,
                           filter_difficulty=difficulty,
                           notifications=notifications)


@recipes_bp.route('/<int:id>')
@login_required
def detail(id):
    user_id = session['user_id']
    recipe = Recipe.query.get_or_404(id)
    ingredient_status = get_recipe_ingredient_status(id, user_id)

    # can_cook if at least one ingredient is available or expiring
    can_cook = any(s['status'] in ['available', 'expiring'] for s in ingredient_status)

    notifications = _get_notifications(user_id)

    return render_template('recipe_detail.html',
                           recipe=recipe,
                           ingredient_status=ingredient_status,
                           can_cook=can_cook,
                           notifications=notifications)


@recipes_bp.route('/<int:id>/use', methods=['POST'])
@login_required
def use_ingredients(id):
    recipe = Recipe.query.get_or_404(id)
    user_id = session['user_id']

    ingredient_status = get_recipe_ingredient_status(id, user_id)

    count = 0
    for stat in ingredient_status:
        if stat['status'] in ['available', 'expiring'] and stat['pantry_item']:
            p_item = db.session.get(PantryItem, stat['pantry_item'].id)
            if p_item:
                p_item.status = 'consumed'
                p_item.quantity = 0
                count += 1

    db.session.commit()
    flash(f'Cooked "{recipe.name}"! {count} pantry item(s) marked as used. Great job reducing food waste! ♻️', 'success')
    return redirect(url_for('pantry.list_items'))
