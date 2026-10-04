from flask import Blueprint, render_template, session
from utils import login_required
from services.expiry_service import get_pantry_summary
from services.recommendation_service import get_recommendations
from services.analytics_service import get_waste_analytics
from models.pantry import PantryItem
import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = session['user_id']

    summary = get_pantry_summary(user_id)

    items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    expiring_items = [i for i in items if i.days_remaining <= 7]
    expiring_items.sort(key=lambda x: x.days_remaining)
    top_expiring = expiring_items[:5]

    recommended_recipes = get_recommendations(user_id, limit=6)

    analytics = get_waste_analytics(user_id)

    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = 'Morning'
    elif hour < 18:
        greeting = 'Afternoon'
    else:
        greeting = 'Evening'

    notifications = {
        'expiring_count': summary.get('expiring_soon_count', 0),
        'expired_count': summary.get('expired_count', 0),
        'recipes_available': len(recommended_recipes)
    }

    return render_template('dashboard.html',
                           user_name=session.get('user_name', 'User'),
                           greeting=greeting,
                           total_items=summary.get('total_items', 0),
                           fresh_count=summary.get('fresh_count', 0),
                           expiring_soon_count=summary.get('expiring_soon_count', 0),
                           expired_count=summary.get('expired_count', 0),
                           wasted_count=summary.get('wasted_count', 0),
                           top_expiring=top_expiring,
                           recommended_recipes=recommended_recipes,
                           analytics=analytics,
                           notifications=notifications)
