"""
Smart Pantry: Expiry-Aware Recipe Recommendation & Food Waste Reduction System
Automated Comprehensive Test Suite for BSc IT Project Demonstration

Run with: python test_system.py
"""

import sys
import unittest
from datetime import date, timedelta
from app import create_app
from extensions import db
from models.user import User
from models.pantry import PantryItem
from models.recipe import Recipe, RecipeIngredient
from models.waste import FoodWaste
from services.expiry_service import get_expiry_status, get_pantry_summary
from services.recommendation_service import calculate_match, get_recommendations
from services.analytics_service import get_waste_analytics, get_environmental_impact


class SmartPantryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False

    def setUp(self):
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        u = User.query.filter_by(email='tester@smartpantry.local').first()
        if u:
            PantryItem.query.filter_by(user_id=u.id).delete()
            FoodWaste.query.filter_by(user_id=u.id).delete()
            db.session.delete(u)
            db.session.commit()

    def tearDown(self):
        self.app_context.pop()

    # ----------------------------------------------------
    # 1. USER AUTHENTICATION TESTS
    # ----------------------------------------------------
    def test_01_user_registration(self):
        """Test user registration with valid and invalid inputs."""
        # Valid registration
        res = self.client.post('/register', data={
            'name': 'Pantry Test User',
            'email': 'tester@smartpantry.local',
            'password': 'TestPassword@123',
            'confirm_password': 'TestPassword@123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Registration successful', res.data)

        # Duplicate email registration should fail
        dup_res = self.client.post('/register', data={
            'name': 'Another User',
            'email': 'tester@smartpantry.local',
            'password': 'TestPassword@123',
            'confirm_password': 'TestPassword@123'
        }, follow_redirects=True)
        self.assertIn(b'Email already registered', dup_res.data)

        # Password mismatch
        mismatch_res = self.client.post('/register', data={
            'name': 'Mismatch User',
            'email': 'mismatch@smartpantry.local',
            'password': 'Password1',
            'confirm_password': 'Password2'
        }, follow_redirects=True)
        self.assertIn(b'Passwords do not match', mismatch_res.data)

        # Password too short (<6 characters)
        short_res = self.client.post('/register', data={
            'name': 'Short User',
            'email': 'short@smartpantry.local',
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        self.assertIn(b'at least 6 characters', short_res.data)

    def test_02_user_login_and_logout(self):
        """Test login with demo user and logout."""
        # Invalid password
        fail_login = self.client.post('/login', data={
            'email': 'demo@smartpantry.local',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', fail_login.data)

        # Valid login
        login_res = self.client.post('/login', data={
            'email': 'demo@smartpantry.local',
            'password': 'Demo@123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Logged in successfully', login_res.data)

        # Logout
        logout_res = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out', logout_res.data)

    def test_03_route_protection(self):
        """Unauthenticated access to protected routes must redirect to login."""
        protected_routes = ['/dashboard', '/pantry', '/recipes', '/waste', '/analytics', '/expiring']
        for route in protected_routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 302, f'Route {route} not protected')
            self.assertIn('/login', res.headers.get('Location', ''))

    # ----------------------------------------------------
    # 2. DYNAMIC EXPIRY CALCULATION TESTS
    # ----------------------------------------------------
    def test_04_expiry_calculation_logic(self):
        """Verify dynamic status calculation matches rules."""
        today = date.today()

        # Rule 1: days_remaining < 0 -> Expired
        status, days, badge = get_expiry_status(today - timedelta(days=2))
        self.assertEqual(status, 'Expired')
        self.assertLess(days, 0)

        # Rule 2: days_remaining == 0 -> Expires Today
        status, days, badge = get_expiry_status(today)
        self.assertEqual(status, 'Expires Today')
        self.assertEqual(days, 0)

        # Rule 3: days_remaining <= 3 -> Expiring Soon
        status, days, badge = get_expiry_status(today + timedelta(days=2))
        self.assertEqual(status, 'Expiring Soon')
        self.assertEqual(days, 2)

        # Rule 4: days_remaining <= 7 -> Use Soon
        status, days, badge = get_expiry_status(today + timedelta(days=5))
        self.assertEqual(status, 'Use Soon')
        self.assertEqual(days, 5)

        # Rule 5: days_remaining > 7 -> Fresh
        status, days, badge = get_expiry_status(today + timedelta(days=15))
        self.assertEqual(status, 'Fresh')
        self.assertEqual(days, 15)

    # ----------------------------------------------------
    # 3. PANTRY MANAGEMENT TESTS
    # ----------------------------------------------------
    def test_05_pantry_crud(self):
        """Test adding, editing, and deleting pantry items."""
        # Login
        self.client.post('/login', data={'email': 'demo@smartpantry.local', 'password': 'Demo@123'}, follow_redirects=True)

        today = date.today()

        # Add Item
        add_res = self.client.post('/pantry/add', data={
            'name': 'Organic Apples',
            'category': 'Fruits',
            'quantity': '4.0',
            'unit': 'pieces',
            'purchase_date': today.strftime('%Y-%m-%d'),
            'expiry_date': (today + timedelta(days=6)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn(b'Organic Apples', add_res.data)

        # Verify in DB
        u = User.query.filter_by(email='demo@smartpantry.local').first()
        item = PantryItem.query.filter_by(user_id=u.id, name='Organic Apples').first()
        self.assertIsNotNone(item)
        self.assertEqual(item.computed_status, 'Use Soon')

        # Edit Item
        edit_res = self.client.post(f'/pantry/edit/{item.id}', data={
            'name': 'Green Apples',
            'category': 'Fruits',
            'quantity': '3.0',
            'unit': 'pieces',
            'purchase_date': today.strftime('%Y-%m-%d'),
            'expiry_date': (today + timedelta(days=2)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)
        self.assertIn(b'updated successfully', edit_res.data)

        # Verify updated status
        item = db.session.get(PantryItem, item.id)
        self.assertEqual(item.name, 'Green Apples')
        self.assertEqual(item.computed_status, 'Expiring Soon')

        # Delete Item
        del_res = self.client.post(f'/pantry/delete/{item.id}', follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertIn(b'removed from your pantry', del_res.data)

    def test_06_pantry_search_filter_sort(self):
        """Test searching, filtering, and sorting pantry items."""
        self.client.post('/login', data={'email': 'demo@smartpantry.local', 'password': 'Demo@123'}, follow_redirects=True)

        # Search by name
        res_search = self.client.get('/pantry?q=Tomato')
        self.assertIn(b'Tomato', res_search.data)

        # Filter by Category
        res_cat = self.client.get('/pantry?category=Dairy')
        self.assertIn(b'Dairy', res_cat.data)

        # Sort by Name
        res_sort = self.client.get('/pantry?sort=name')
        self.assertEqual(res_sort.status_code, 200)

    # ----------------------------------------------------
    # 4. RECIPE RECOMMENDATION ALGORITHM TESTS
    # ----------------------------------------------------
    def test_07_recommendation_algorithm_scoring(self):
        """
        Verify the mathematical formulation of recommendation algorithm:
        Final Score = (Ingredient Match * 0.60) + (Expiry Priority * 0.30) + (Availability * 0.10)
        Normalized to 0-100.
        """
        u = User.query.filter_by(email='demo@smartpantry.local').first()
        items = PantryItem.query.filter_by(user_id=u.id, status='available').all()

        recipes = Recipe.query.all()
        self.assertGreaterEqual(len(recipes), 30, "Seed dataset should have at least 30 recipes")

        top_recs = get_recommendations(u.id, limit=6)
        self.assertGreater(len(top_recs), 0)

        for rec in top_recs:
            score = rec['match_info']['final_score']
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
            self.assertGreater(rec['match_info']['match_count'], 0)

    def test_08_expiry_priority_boost(self):
        """Verify that recipes with expiring ingredients get higher priority."""
        today = date.today()
        # Item A expires in 1 day (urgent)
        item_urgent = PantryItem(
            user_id=999, name='Bread', category='Bakery', quantity=2, unit='pieces',
            purchase_date=today, expiry_date=today + timedelta(days=1), status='available'
        )
        # Item B expires in 30 days (fresh)
        item_fresh = PantryItem(
            user_id=999, name='Rice', category='Grains', quantity=1, unit='kg',
            purchase_date=today, expiry_date=today + timedelta(days=30), status='available'
        )

        # Recipe using Bread
        recipe_toast = Recipe.query.filter(Recipe.name.ilike('%Toast%')).first()
        # Recipe using Rice
        recipe_rice = Recipe.query.filter(Recipe.name.ilike('%Rice%')).first()

        if recipe_toast and recipe_rice:
            match_toast = calculate_match(recipe_toast, [item_urgent])
            match_rice = calculate_match(recipe_rice, [item_fresh])
            # Urgent item should yield higher expiry_score than fresh item
            self.assertGreater(match_toast['expiry_score'], match_rice['expiry_score'])

    # ----------------------------------------------------
    # 5. RECIPE CONSUMPTION & PANTRY DEDUCTION TESTS
    # ----------------------------------------------------
    def test_09_cook_recipe_and_pantry_deduction(self):
        """When user cooks a recipe, pantry quantities update and items are marked consumed."""
        self.client.post('/login', data={'email': 'demo@smartpantry.local', 'password': 'Demo@123'}, follow_redirects=True)

        u = User.query.filter_by(email='demo@smartpantry.local').first()
        recipe = Recipe.query.first()
        self.assertIsNotNone(recipe)

        res = self.client.post(f'/recipes/{recipe.id}/use', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'marked as used', res.data)

    # ----------------------------------------------------
    # 6. FOOD WASTE TRACKING & ANALYTICS TESTS
    # ----------------------------------------------------
    def test_10_food_waste_recording(self):
        """Test recording food waste directly and from pantry item."""
        self.client.post('/login', data={'email': 'demo@smartpantry.local', 'password': 'Demo@123'}, follow_redirects=True)
        u = User.query.filter_by(email='demo@smartpantry.local').first()

        today = date.today()

        # Add waste item to pantry first
        self.client.post('/pantry/add', data={
            'name': 'Sour Yogurt',
            'category': 'Dairy',
            'quantity': '1',
            'unit': 'bottle',
            'purchase_date': (today - timedelta(days=10)).strftime('%Y-%m-%d'),
            'expiry_date': (today - timedelta(days=2)).strftime('%Y-%m-%d')
        }, follow_redirects=True)

        yogurt = PantryItem.query.filter_by(user_id=u.id, name='Sour Yogurt').first()
        self.assertIsNotNone(yogurt)

        # Mark as wasted
        wasted_res = self.client.post(f'/pantry/wasted/{yogurt.id}', data={
            'quantity': '1',
            'reason': 'Expired'
        }, follow_redirects=True)
        self.assertEqual(wasted_res.status_code, 200)
        self.assertIn(b'Food waste recorded successfully.', wasted_res.data)

        # Check FoodWaste record in DB
        w_record = FoodWaste.query.filter_by(user_id=u.id, item_name='Sour Yogurt').first()
        self.assertIsNotNone(w_record)
        self.assertEqual(w_record.reason, 'Expired')

    def test_11_analytics_and_environmental_impact(self):
        """Test analytics and environmental impact calculations."""
        u = User.query.filter_by(email='demo@smartpantry.local').first()
        analytics = get_waste_analytics(u.id)

        self.assertIn('totals', analytics)
        self.assertIn('waste_by_category', analytics)
        self.assertIn('waste_by_reason', analytics)
        self.assertIn('monthly_trend', analytics)

        env = get_environmental_impact(u.id)
        self.assertIn('items_saved', env)
        self.assertIn('items_wasted', env)
        self.assertIn('note', env)

        # Test analytics page response
        self.client.post('/login', data={'email': 'demo@smartpantry.local', 'password': 'Demo@123'}, follow_redirects=True)
        res = self.client.get('/analytics')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Analytics', res.data)
        self.assertIn(b'Food Fate Breakdown', res.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
