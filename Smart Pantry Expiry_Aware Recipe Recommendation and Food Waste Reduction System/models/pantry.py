from extensions import db
from datetime import date
from sqlalchemy.orm import relationship

class PantryItem(db.Model):
    __tablename__ = 'pantry_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='available')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = relationship('User', backref='pantry_items')

    CATEGORIES = ['Dairy', 'Fruits', 'Vegetables', 'Grains', 'Bakery', 'Meat', 'Seafood', 'Frozen', 'Beverages', 'Snacks', 'Spices', 'Other']
    UNITS = ['pieces', 'kg', 'g', 'litre', 'ml', 'packet', 'bottle', 'box']

    @property
    def days_remaining(self):
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return 0

    @property
    def computed_status(self):
        if self.status != 'available':
            return self.status
        days = self.days_remaining
        if days < 0:
            return 'Expired'
        elif days == 0:
            return 'Expires Today'
        elif days <= 3:
            return 'Expiring Soon'
        elif days <= 7:
            return 'Use Soon'
        else:
            return 'Fresh'
