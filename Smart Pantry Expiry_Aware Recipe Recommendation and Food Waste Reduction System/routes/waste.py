from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.waste import FoodWaste
from models.pantry import PantryItem
from extensions import db
from utils import login_required
from datetime import datetime, date

waste_bp = Blueprint('waste', __name__, url_prefix='/waste')


def _get_notifications(user_id):
    from services.expiry_service import get_pantry_summary
    summary = get_pantry_summary(user_id)
    return {
        'expiring_count': summary.get('expiring_soon_count', 0),
        'expired_count': summary.get('expired_count', 0),
    }


@waste_bp.route('')
@waste_bp.route('/')
@login_required
def list_waste():
    user_id = session['user_id']
    records = FoodWaste.query.filter_by(user_id=user_id).order_by(FoodWaste.waste_date.desc()).all()
    notifications = _get_notifications(user_id)
    return render_template('waste.html',
                           records=records,
                           reasons=FoodWaste.REASONS,
                           units=PantryItem.UNITS,
                           waste_item=None,
                           notifications=notifications)


@waste_bp.route('/add', methods=['POST'])
@login_required
def add():
    user_id = session['user_id']
    try:
        item_name = request.form.get('item_name', '').strip()
        quantity_str = request.form.get('quantity', '').strip()
        unit = request.form.get('unit', 'pieces').strip()
        reason = request.form.get('reason', 'Other').strip()
        waste_date_str = request.form.get('waste_date', '').strip()

        if not item_name:
            flash('Item name is required.', 'danger')
            return redirect(url_for('waste.list_waste'))

        quantity = float(quantity_str) if quantity_str else 1.0
        waste_date_val = datetime.strptime(waste_date_str, '%Y-%m-%d').date() if waste_date_str else date.today()

        record = FoodWaste(
            user_id=user_id,
            item_name=item_name,
            quantity=quantity,
            unit=unit,
            reason=reason,
            waste_date=waste_date_val
        )
        db.session.add(record)
        db.session.commit()
        flash(f'Waste record for "{item_name}" added.', 'success')
    except Exception as ex:
        db.session.rollback()
        flash(f'Error recording waste: {str(ex)}', 'danger')

    return redirect(url_for('waste.list_waste'))


@waste_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    record = FoodWaste.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    item_name = record.item_name
    db.session.delete(record)
    db.session.commit()
    flash(f'Waste record for "{item_name}" deleted.', 'info')
    return redirect(url_for('waste.list_waste'))
