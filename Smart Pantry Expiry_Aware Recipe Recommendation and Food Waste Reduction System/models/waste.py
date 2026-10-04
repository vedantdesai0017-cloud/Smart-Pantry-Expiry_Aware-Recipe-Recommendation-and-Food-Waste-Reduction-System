from extensions import db
from sqlalchemy.orm import relationship

class FoodWaste(db.Model):
    __tablename__ = 'food_waste'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pantry_item_id = db.Column(db.Integer, db.ForeignKey('pantry_items.id'), nullable=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(50), nullable=False)
    waste_date = db.Column(db.Date, nullable=False)

    user = relationship('User', backref='wasted_items')
    pantry_item = relationship('PantryItem')

    REASONS = ['Expired', 'Spoiled', 'Over-purchased', 'Not used', 'Other']
