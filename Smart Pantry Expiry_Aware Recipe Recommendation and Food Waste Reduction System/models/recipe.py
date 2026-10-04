from extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    instructions = db.Column(db.Text, nullable=False)
    cooking_time = db.Column(db.Integer)
    difficulty = db.Column(db.String(20))
    image = db.Column(db.String(300), nullable=True)
    dietary_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ingredients = relationship('RecipeIngredient', backref='recipe', cascade="all, delete-orphan")

class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    ingredient_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(50))
    unit = db.Column(db.String(20))
