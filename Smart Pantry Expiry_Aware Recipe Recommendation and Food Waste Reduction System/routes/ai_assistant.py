from flask import Blueprint, render_template, request, jsonify, session
from utils import login_required
from models.pantry import PantryItem
from services.ai_service import (
    ask_pantry_ai,
    get_ai_recipe_recommendations,
    generate_recipe,
    suggest_ingredient_substitutions,
    build_pantry_context
)
from services.expiry_service import get_pantry_summary

ai_bp = Blueprint('ai', __name__)


def _get_notifications(user_id):
    summary = get_pantry_summary(user_id)
    return {
        'expiring_count': summary.get('expiring_soon_count', 0),
        'expired_count': summary.get('expired_count', 0),
    }


@ai_bp.route('/ai-assistant')
@login_required
def assistant():
    user_id = session['user_id']
    pantry_items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    context = build_pantry_context(pantry_items)
    notifications = _get_notifications(user_id)

    quick_prompts = [
        "What should I cook today?",
        "What expires soon?",
        "Give me a quick recipe.",
        "Use my ingredients to make a healthy meal.",
        "What can I cook without buying anything?"
    ]

    return render_template(
        'ai_assistant.html',
        pantry_count=len(pantry_items),
        expiring_items=context["expiring_soon"],
        notifications=notifications,
        quick_prompts=quick_prompts
    )


@ai_bp.route('/api/ai/chat', methods=['POST'])
@login_required
def chat():
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({
            'status': 'error',
            'message': 'Please provide a message or recipe question.'
        }), 400

    pantry_items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    ai_result = ask_pantry_ai(user_message, pantry_items)

    return jsonify({
        'status': 'success',
        'response': ai_result.get('message'),
        'has_recipe': ai_result.get('has_recipe', False),
        'structured_recipe': ai_result.get('structured_recipe'),
        'is_fallback': ai_result.get('is_fallback', False),
        'pantry_count': ai_result.get('pantry_count', len(pantry_items)),
        'expiring_count': ai_result.get('expiring_count', 0)
    })


@ai_bp.route('/api/ai/recommend', methods=['GET'])
@login_required
def recommend():
    user_id = session['user_id']
    pantry_items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    ai_result = get_ai_recipe_recommendations(pantry_items, limit=3)
    return jsonify(ai_result)


@ai_bp.route('/api/ai/pantry-context', methods=['GET'])
@login_required
def pantry_context():
    """Returns the structured privacy-safe context prepared for AI."""
    user_id = session['user_id']
    pantry_items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    context = build_pantry_context(pantry_items)
    return jsonify({
        'status': 'success',
        'context': context
    })
