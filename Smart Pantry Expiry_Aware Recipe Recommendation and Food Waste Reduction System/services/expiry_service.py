from models.pantry import PantryItem
from datetime import date

def get_expiry_status(expiry_date):
    if not expiry_date:
        return 'Unknown', 0, 'bg-secondary'
    
    days = (expiry_date - date.today()).days
    if days < 0:
        return 'Expired', days, 'bg-danger'
    elif days == 0:
        return 'Expires Today', days, 'bg-danger'
    elif days <= 3:
        return 'Expiring Soon', days, 'bg-warning'
    elif days <= 7:
        return 'Use Soon', days, 'bg-info text-dark'
    else:
        return 'Fresh', days, 'bg-success'

def get_expiring_items(user_id, days=7):
    items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    return [i for i in items if i.days_remaining <= days and i.days_remaining >= 0]

def get_expired_items(user_id):
    items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    return [i for i in items if i.days_remaining < 0]

def get_pantry_summary(user_id):
    items = PantryItem.query.filter_by(user_id=user_id, status='available').all()
    total = len(items)
    
    fresh = 0
    expiring_soon = 0
    expired = 0
    
    for item in items:
        status = item.computed_status
        if status in ['Fresh', 'Use Soon']:
            fresh += 1
        elif status in ['Expiring Soon', 'Expires Today']:
            expiring_soon += 1
        elif status == 'Expired':
            expired += 1
            
    wasted_count = PantryItem.query.filter_by(user_id=user_id, status='wasted').count()
    consumed_count = PantryItem.query.filter_by(user_id=user_id, status='consumed').count()

    return {
        'total_items': total,
        'fresh_count': fresh,
        'expiring_soon_count': expiring_soon,
        'expired_count': expired,
        'wasted_count': wasted_count,
        'consumed_count': consumed_count,
    }
