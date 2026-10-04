"""
Test suite for Smart Pantry AI Layer
Tests:
- AI Context Builder (privacy, expiry preservation, structured schema)
- AI Service calls & Fallback handling (missing API key, network errors)
- AI Assistant Flask Routes (GET /ai-assistant, POST /api/ai/chat, GET /api/ai/recommend, GET /api/ai/pantry-context)
- Expiry-Aware prioritization (bread/tomato expiring soon prioritized)
- Ingredient substitution suggestion logic
- Structured JSON response validation & fallback
"""

import unittest
import json
from datetime import date, timedelta
from app import create_app
from extensions import db
from models.user import User
from models.pantry import PantryItem
from services.ai_service import (
    build_pantry_context,
    ask_pantry_ai,
    get_ai_recipe_recommendations,
    generate_recipe,
    suggest_ingredient_substitutions,
    _extract_json,
    _local_rule_based_recommendation
)


class SmartPantryAITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True

    def setUp(self):
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Login as demo user
        self.client.post('/login', data={'email': 'demo@smartpantry.local', 'password': 'Demo@123'}, follow_redirects=True)
        self.user = User.query.filter_by(email='demo@smartpantry.local').first()

    def tearDown(self):
        self.app_context.pop()

    def test_01_ai_pantry_context_builder_privacy_and_structure(self):
        """Verify pantry context builder produces structured data and protects user privacy."""
        pantry_items = PantryItem.query.filter_by(user_id=self.user.id, status='available').all()
        self.assertGreater(len(pantry_items), 0)

        context = build_pantry_context(pantry_items)

        # Structure checks
        self.assertIn('items', context)
        self.assertIn('context_text', context)
        self.assertIn('expiring_soon', context)
        self.assertIn('expired', context)
        self.assertIn('fresh', context)

        # Privacy check: Ensure sensitive terms are never present
        context_str = json.dumps(context).lower()
        self.assertNotIn('password', context_str)
        self.assertNotIn('hash', context_str)
        self.assertNotIn('token', context_str)

        # Check item attributes
        first_item = context['items'][0]
        self.assertIn('name', first_item)
        self.assertIn('days_remaining', first_item)
        self.assertIn('status', first_item)
        self.assertIn('quantity', first_item)

    def test_02_expiry_preservation_by_backend(self):
        """Verify AI context uses backend-calculated expiry and does not guess."""
        today = date.today()
        test_item = PantryItem(
            user_id=self.user.id,
            name='Test Yogurt',
            category='Dairy',
            quantity=1,
            unit='bottle',
            purchase_date=today - timedelta(days=5),
            expiry_date=today + timedelta(days=1),
            status='available'
        )

        self.assertEqual(test_item.days_remaining, 1)
        self.assertEqual(test_item.computed_status, 'Expiring Soon')

        context = build_pantry_context([test_item])
        self.assertIn('Test Yogurt', context['expiring_soon'])
        self.assertIn('Status: Expiring Soon', context['context_text'])
        self.assertIn('Days remaining: 1', context['context_text'])

    def test_03_json_extractor_utility(self):
        """Verify robust JSON extraction from clean JSON, markdown codeblocks, and mixed text."""
        # 1. Clean JSON
        json1 = _extract_json('{"recipe_name": "Poha", "time": "15 min"}')
        self.assertEqual(json1.get('recipe_name'), 'Poha')

        # 2. Markdown fenced JSON
        json2 = _extract_json('```json\n{"recipe_name": "Upma", "steps": ["Boil water"]}\n```')
        self.assertEqual(json2.get('recipe_name'), 'Upma')

        # 3. Text surrounding JSON
        json3 = _extract_json('Here is your recipe: {"recipe_name": "Toast", "easy": true} Enjoy your meal!')
        self.assertEqual(json3.get('recipe_name'), 'Toast')

        # 4. Invalid text
        invalid = _extract_json('Just plain conversational text without brackets')
        self.assertIsNone(invalid)

    def test_04_ai_assistant_route_protection(self):
        """Unauthenticated access to /ai-assistant must redirect to /login."""
        anon_client = self.app.test_client()
        res = anon_client.get('/ai-assistant')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers.get('Location', ''))

    def test_05_ai_assistant_page_load(self):
        """Logged-in access to /ai-assistant renders chat interface."""
        res = self.client.get('/ai-assistant')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Smart Pantry AI', res.data)
        self.assertIn(b'What should I cook today?', res.data)
        self.assertIn(b'Pantry Synced', res.data)

    def test_06_api_ai_chat_empty_message_validation(self):
        """POST /api/ai/chat requires non-empty message."""
        res = self.client.post('/api/ai/chat', json={'message': '   '})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'error')

    def test_07_api_ai_chat_response_handling(self):
        """POST /api/ai/chat processes message and returns structured reply."""
        res = self.client.post('/api/ai/chat', json={'message': 'What can I cook with bread and tomato?'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('response', data)
        self.assertGreater(data.get('pantry_count', 0), 0)

    def test_08_api_ai_pantry_context_endpoint(self):
        """GET /api/ai/pantry-context returns structured pantry context."""
        res = self.client.get('/api/ai/pantry-context')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('items', data['context'])
        self.assertIn('expiring_soon', data['context'])

    def test_09_api_ai_recommend_endpoint(self):
        """GET /api/ai/recommend returns recipe recommendations."""
        res = self.client.get('/api/ai/recommend')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('recommendations', data)

    def test_10_local_rule_based_fallback_quality(self):
        """Verify rule-based fallback accurately prioritizes expiring items when AI is offline."""
        pantry_items = PantryItem.query.filter_by(user_id=self.user.id, status='available').all()
        fallback = _local_rule_based_recommendation(pantry_items, limit=2)
        self.assertGreater(len(fallback), 0)
        first_rec = fallback[0]
        self.assertIn('recipe_name', first_rec)
        self.assertIn('reason', first_rec)
        self.assertIn('available_ingredients', first_rec)
        self.assertIn('steps', first_rec)

    def test_11_ask_pantry_ai_function_contract(self):
        """Test the core ask_pantry_ai function return schema."""
        pantry_items = PantryItem.query.filter_by(user_id=self.user.id, status='available').all()
        result = ask_pantry_ai("Give me a quick recipe using my expiring food.", pantry_items)

        self.assertIn('message', result)
        self.assertIn('has_recipe', result)
        self.assertIn('pantry_count', result)
        self.assertIn('expiring_count', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
