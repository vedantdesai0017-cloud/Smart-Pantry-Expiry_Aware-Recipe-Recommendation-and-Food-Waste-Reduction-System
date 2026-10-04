from flask import Blueprint, render_template, session
from utils import login_required
from models.pantry import PantryItem

expiring_bp = Blueprint('expiring', __name__, url_prefix='/expiring')


def _get_notifications(user_id):
    from services.expiry_service import get_pantry_summary
    summary = get_pantry_summary(user_id)
    return {
        'expiring_count': summary.get('expiring_soon_count', 0),
        'expired_count': summary.get('expired_count', 0),
    }


@expiring_bp.route('')
@expiring_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    items = PantryItem.query.filter_by(user_id=user_id, status='available').all()

    expired = []
    today = []
    high_priority = []
    medium_priority = []

    for item in items:
        days = item.days_remaining
        if days < 0:
            expired.append(item)
        elif days == 0:
            today.append(item)
        elif 1 <= days <= 3:
            high_priority.append(item)
        elif 4 <= days <= 7:
            medium_priority.append(item)

    expired.sort(key=lambda x: x.days_remaining)
    today.sort(key=lambda x: x.name)
    high_priority.sort(key=lambda x: x.days_remaining)
    medium_priority.sort(key=lambda x: x.days_remaining)

    notifications = _get_notifications(user_id)

    return render_template('expiring.html',
                           expired=expired,
                           today=today,
                           high_priority=high_priority,
                           medium_priority=medium_priority,
                           notifications=notifications)
