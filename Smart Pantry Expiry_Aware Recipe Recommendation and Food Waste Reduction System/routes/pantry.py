from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.pantry import PantryItem
from models.waste import FoodWaste
from extensions import db
from utils import login_required
from datetime import datetime, date

pantry_bp = Blueprint('pantry', __name__, url_prefix='/pantry')


@pantry_bp.route('')
@pantry_bp.route('/')
@login_required
def list_items():
    user_id = session['user_id']
    query = PantryItem.query.filter_by(user_id=user_id)

    search = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip()
    sort_by = request.args.get('sort', 'expiry_date')

    if search:
        query = query.filter(PantryItem.name.ilike(f'%{search}%'))
    if category:
        query = query.filter(PantryItem.category == category)

    # Get all (we filter by computed_status in Python)
    items = query.all()

    # Filter by computed status if requested
    if status_filter:
        items = [i for i in items if i.computed_status.lower().replace(' ', '_') == status_filter.lower().replace(' ', '_')
                 or i.computed_status.lower() == status_filter.lower()]

    # Sort
    if sort_by == 'name':
        items.sort(key=lambda x: x.name.lower())
    elif sort_by == 'category':
        items.sort(key=lambda x: x.category.lower())
    else:
        items.sort(key=lambda x: x.expiry_date)

    notifications = _get_notifications(user_id)

    return render_template('pantry.html',
                           items=items,
                           categories=PantryItem.CATEGORIES,
                           units=PantryItem.UNITS,
                           search_query=search,
                           filter_category=category,
                           filter_status=status_filter,
                           sort_by=sort_by,
                           notifications=notifications)


@pantry_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user_id = session['user_id']
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            quantity_str = request.form.get('quantity', '').strip()
            unit = request.form.get('unit', '').strip()
            purchase_date_str = request.form.get('purchase_date', '').strip()
            expiry_date_str = request.form.get('expiry_date', '').strip()

            errors = []
            if not name:
                errors.append('Food name is required.')
            if not category:
                errors.append('Category is required.')
            if not quantity_str:
                errors.append('Quantity is required.')
            else:
                try:
                    quantity = float(quantity_str)
                    if quantity <= 0:
                        errors.append('Quantity must be positive.')
                except ValueError:
                    errors.append('Quantity must be a number.')
                    quantity = 0
            if not purchase_date_str:
                errors.append('Purchase date is required.')
            if not expiry_date_str:
                errors.append('Expiry date is required.')

            if errors:
                for e in errors:
                    flash(e, 'danger')
                return render_template('add_item.html',
                                       categories=PantryItem.CATEGORIES,
                                       units=PantryItem.UNITS,
                                       notifications=_get_notifications(user_id))

            purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()

            if expiry_date < purchase_date:
                flash('Expiry date cannot be before purchase date.', 'danger')
                return render_template('add_item.html',
                                       categories=PantryItem.CATEGORIES,
                                       units=PantryItem.UNITS,
                                       notifications=_get_notifications(user_id))

            item = PantryItem(
                user_id=user_id,
                name=name,
                category=category,
                quantity=quantity,
                unit=unit,
                purchase_date=purchase_date,
                expiry_date=expiry_date,
                status='available'
            )
            db.session.add(item)
            db.session.commit()
            flash(f'"{name}" added to your pantry successfully!', 'success')
            return redirect(url_for('pantry.list_items'))

        except Exception as ex:
            db.session.rollback()
            flash(f'Error adding item: {str(ex)}', 'danger')

    return render_template('add_item.html',
                           categories=PantryItem.CATEGORIES,
                           units=PantryItem.UNITS,
                           notifications=_get_notifications(user_id))


@pantry_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    user_id = session['user_id']
    item = PantryItem.query.filter_by(id=id, user_id=user_id).first_or_404()

    if request.method == 'POST':
        try:
            item.name = request.form.get('name', '').strip()
            item.category = request.form.get('category', '').strip()
            item.quantity = float(request.form.get('quantity', 0))
            item.unit = request.form.get('unit', '').strip()
            item.purchase_date = datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date()
            item.expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
            db.session.commit()
            flash(f'"{item.name}" updated successfully!', 'success')
            return redirect(url_for('pantry.list_items'))
        except Exception as ex:
            db.session.rollback()
            flash(f'Error updating item: {str(ex)}', 'danger')

    return render_template('edit_item.html',
                           item=item,
                           categories=PantryItem.CATEGORIES,
                           units=PantryItem.UNITS,
                           notifications=_get_notifications(user_id))


@pantry_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    item = PantryItem.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f'"{name}" removed from your pantry.', 'info')
    return redirect(url_for('pantry.list_items'))


@pantry_bp.route('/used/<int:id>', methods=['POST'])
@login_required
def used(id):
    item = PantryItem.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    used_qty_str = request.form.get('quantity')
    if used_qty_str:
        used_qty = float(used_qty_str)
        item.quantity -= used_qty
        if item.quantity <= 0:
            item.status = 'consumed'
            item.quantity = 0
    else:
        item.status = 'consumed'
        item.quantity = 0
    db.session.commit()

    if request.is_json:
        return jsonify({'status': 'success'})

    flash(f'"{item.name}" marked as used. Great job reducing waste!', 'success')
    return redirect(url_for('pantry.list_items'))


@pantry_bp.route('/wasted/<int:id>', methods=['GET', 'POST'])
@login_required
def wasted(id):
    user_id = session['user_id']
    item = PantryItem.query.filter_by(id=id, user_id=user_id).first_or_404()
    if request.method == 'POST':
        try:
            qty = float(request.form.get('quantity', item.quantity))
            reason = request.form.get('reason', 'Other')

            waste_record = FoodWaste(
                user_id=user_id,
                pantry_item_id=item.id,
                item_name=item.name,
                quantity=qty,
                unit=item.unit,
                reason=reason,
                waste_date=date.today()
            )
            db.session.add(waste_record)

            item.quantity -= qty
            if item.quantity <= 0:
                item.status = 'wasted'
                item.quantity = 0

            db.session.commit()

            if request.is_json:
                return jsonify({'status': 'success'})

            flash('Food waste recorded successfully.', 'warning')
            return redirect(url_for('pantry.list_items'))
        except Exception as ex:
            db.session.rollback()
            flash(f'Error recording waste: {str(ex)}', 'danger')

    return render_template('waste.html',
                           waste_item=item,
                           reasons=FoodWaste.REASONS,
                           records=FoodWaste.query.filter_by(user_id=user_id).order_by(FoodWaste.waste_date.desc()).all(),
                           units=PantryItem.UNITS,
                           notifications=_get_notifications(user_id))


def _get_notifications(user_id):
    """Helper to build notification counts."""
    from services.expiry_service import get_pantry_summary
    summary = get_pantry_summary(user_id)
    return {
        'expiring_count': summary.get('expiring_soon_count', 0),
        'expired_count': summary.get('expired_count', 0),
    }
