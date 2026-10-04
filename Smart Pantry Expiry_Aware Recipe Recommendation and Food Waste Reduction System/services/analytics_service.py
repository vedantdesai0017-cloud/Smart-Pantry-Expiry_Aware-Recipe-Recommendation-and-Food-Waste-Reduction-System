from models.waste import FoodWaste
from models.pantry import PantryItem
from extensions import db
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def get_waste_analytics(user_id):
    waste_records = FoodWaste.query.filter_by(user_id=user_id).all()
    
    waste_by_category = {}
    waste_by_reason = {}
    
    for rec in waste_records:
        reason = rec.reason
        waste_by_reason[reason] = waste_by_reason.get(reason, 0) + rec.quantity
        
        cat = "Unknown"
        if rec.pantry_item:
            cat = rec.pantry_item.category
        waste_by_category[cat] = waste_by_category.get(cat, 0) + rec.quantity
        
    monthly_trend = []
    today = date.today()
    for i in range(5, -1, -1):
        m = today - relativedelta(months=i)
        month_str = m.strftime('%B %Y')
        month_wasted = sum(r.quantity for r in waste_records if r.waste_date.month == m.month and r.waste_date.year == m.year)
        
        monthly_trend.append({
            'month': month_str,
            'wasted': month_wasted,
            'consumed': 0
        })
        
    total_added = PantryItem.query.filter_by(user_id=user_id).count()
    consumed = PantryItem.query.filter_by(user_id=user_id, status='consumed').count()
    wasted = PantryItem.query.filter_by(user_id=user_id, status='wasted').count() + len(waste_records)
    expired = PantryItem.query.filter_by(user_id=user_id).filter(PantryItem.status=='available').all()
    expired_count = sum(1 for i in expired if i.days_remaining < 0)
    
    return {
        'waste_by_category': waste_by_category,
        'waste_by_reason': waste_by_reason,
        'monthly_trend': monthly_trend,
        'totals': {
            'total_added': total_added,
            'consumed': consumed,
            'wasted': wasted,
            'expired_count': expired_count,
            'saved': consumed 
        }
    }

def get_environmental_impact(user_id):
    analytics = get_waste_analytics(user_id)
    saved = analytics['totals']['saved']
    wasted = analytics['totals']['wasted']
    
    return {
        'items_saved': saved,
        'items_wasted': wasted,
        'co2_saved_kg': saved * 0.5,
        'money_saved': saved * 2.0,
        'note': 'These are estimates based on average food item impact.'
    }
