from flask import Blueprint, render_template, session
from utils import login_required
from services.analytics_service import get_waste_analytics, get_environmental_impact
from models.pantry import PantryItem
import json

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


def _get_notifications(user_id):
    from services.expiry_service import get_pantry_summary
    summary = get_pantry_summary(user_id)
    return {
        'expiring_count': summary.get('expiring_soon_count', 0),
        'expired_count': summary.get('expired_count', 0),
    }


@analytics_bp.route('')
@analytics_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    analytics = get_waste_analytics(user_id)
    environmental = get_environmental_impact(user_id)
    notifications = _get_notifications(user_id)

    return render_template('analytics.html',
                           analytics=analytics,
                           analytics_json=json.dumps(analytics),
                           environmental=environmental,
                           notifications=notifications)
