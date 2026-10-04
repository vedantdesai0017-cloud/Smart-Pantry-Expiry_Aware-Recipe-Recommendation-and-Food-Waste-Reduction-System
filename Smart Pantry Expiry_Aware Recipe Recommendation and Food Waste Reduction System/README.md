# 🥦 Smart Pantry: Expiry-Aware Recipe Recommendation & Food Waste Reduction System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-orange.svg)
![Tests](https://img.shields.io/badge/Tests-11%2F11%20Passed-brightgreen.svg)

---

## 📌 Project Overview
**Smart Pantry** is a responsive full-stack web application designed for BSc IT academic capstone and Community Engagement Project (CEP) demonstrations. The core philosophy is:

> **"USE FOOD BEFORE IT BECOMES FOOD WASTE."**

The application enables households to maintain a digital pantry, automatically monitors expiration timelines, generates color-coded dynamic alerts, recommends recipes using an **expiry-prioritized matching engine**, tracks consumed vs. discarded food quantities, and visualizes household environmental impact using interactive Chart.js analytics.

---

## 🚨 Core Problem Addressed
Globally, over 1 billion tonnes of edible food is discarded annually, predominantly in domestic households due to:
1. Forgotten expiration dates of perishable goods in cupboards and refrigerators.
2. Lack of culinary inspiration to combine existing ingredients into meals.
3. Lack of accountability or awareness of personal food waste habits.

Smart Pantry directly eliminates these pain points through proactive notification and smart culinary planning.

---

## ✨ Features
1. **User Authentication & Session Management**: Secure user registration and login with Werkzeug password hashing and protected routes.
2. **Digital Pantry Management**: Track item name, category, quantity, unit, purchase date, and expiry date.
3. **Dynamic Expiry Life Calculation**: Automatically evaluates shelf life on the fly without manual status entry.
4. **Urgent Expiry Alerts**: Visual alerts categorizing items expiring today, within 1–3 days, and within 4–7 days.
5. **Expiry-Aware Recommendation Engine**: Evaluates pantry inventory against 32+ curated recipes, boosting recipes that utilize impending food waste.
6. **One-Click Cooking & Inventory Consumption**: Cook meals and automatically deduct or mark pantry ingredients as consumed.
7. **Food Waste Tracking**: Log spoiled or discarded food with specific reasons (Expired, Spoiled, Over-purchased, etc.).
8. **Interactive Analytics & Dashboards**: Chart.js graphs displaying food fate breakdown, waste reasons, category trends, and monthly tracking.
9. **Environmental Impact Metrics**: Transparent, estimate-labeled summaries of items saved from landfill.
10. **Multi-Criteria Search & Filtering**: Fast client and server-side filtering by dietary type, difficulty, food categories, and expiry status.
11. **🤖 Smart Pantry AI Assistant**: Expiry-aware natural language recipe generation, dynamic culinary reasoning, safe ingredient substitutions, and interactive chat interface powered by Google Gemini.

---

## 🤖 Smart Pantry AI Architecture

The AI layer integrates seamlessly with the existing database and business logic:

```
[ Frontend Chat UI (/ai-assistant) ]
                  │
                  ▼
         [ Flask Backend ]
                  │
                  ▼
         [ Pantry Database ]
                  │
                  ▼
    [ Pantry Context Builder ] ──> Evaluates days_remaining & computed_status (No AI guesswork)
                  │
                  ▼
      [ services/ai_service.py ] ──> Provider Abstraction (Gemini / google-genai SDK / REST)
                  │
                  ▼
            [ AI Model ]
                  │
                  ▼
     [ Structured JSON Schema ] ──> Validates recipe_name, steps, substitutions
                  │
                  ▼
        [ Rich UI Recipe Card ]
```

### Core AI Functions in `services/ai_service.py`:
- `build_pantry_context(pantry_items)`: Generates privacy-safe, structured inventory with backend-verified shelf-life statuses.
- `get_ai_recipe_recommendations(pantry_items)`: Suggests creative recipes prioritizing items closest to expiration.
- `generate_recipe(user_prompt, pantry_items)`: Creates custom step-by-step recipes from natural language questions.
- `suggest_ingredient_substitutions(recipe, pantry_items)`: Provides safe, practical alternatives for missing ingredients using available stock.
- `ask_pantry_ai(user_message, pantry_items)`: Conversational pipeline with structured JSON extraction and zero-downtime offline fallback.

## 🛠️ Technology Stack
- **Backend**: Python 3.8+, Flask 3.0.3
- **ORM & Database**: SQLAlchemy 2.0.31, SQLite (`database.db`)
- **Authentication**: Session-based auth with `werkzeug.security` (PBKDF2 SHA-256)
- **Frontend**: HTML5, CSS3, JavaScript (ES6), Jinja2 Templates
- **UI Framework**: Bootstrap 5.3, Bootstrap Icons 1.11
- **Visualization**: Chart.js 4.4.0 (Doughnut, Bar, and Line charts)
- **Date Utilities**: `python-dateutil`

---

## 📐 Recommendation Algorithm

The recommendation engine compares user pantry items against recipe ingredients using a weighted mathematical scoring formulation:

$$\text{Final Score} = (\text{Ingredient Match} \times 0.60) + (\text{Expiry Priority} \times 0.30) + (\text{Availability Bonus} \times 0.10)$$

Where:
- **Ingredient Match (0.0 – 1.0)**:
  $$\text{Ingredient Match} = \frac{\text{Matched Pantry Ingredients}}{\text{Total Recipe Ingredients}}$$
- **Expiry Priority (0.0 – 1.0)**:
  Evaluates the urgency of the matched ingredients:
  - Expired / Expires Today ($\le 0$ days): **1.00 weight**
  - High Priority ($1 \le \text{days} \le 3$): **0.85 weight**
  - Medium Priority ($4 \le \text{days} \le 7$): **0.60 weight**
  - Fresh / Stable ($> 7$ days): **0.20 weight**
  $$\text{Expiry Priority} = \frac{\sum \text{Weights of Matched Ingredients}}{\text{Total Recipe Ingredients}}$$
- **Availability Bonus (0.0 – 1.0)**:
  If match percentage $\ge 50\%$, bonus = $1.0$; otherwise $\text{match} \times 2.0$.
- **Normalized Final Score**: Scaled to **0 – 100 integer points** for intuitive user display.

---

## ⏱️ Dynamic Expiry Detection Logic

Shelf life is dynamically computed on every query using:
$$\text{days\_remaining} = \text{expiry\_date} - \text{current\_date}$$

| Remaining Days | Computed Status | Visual Indicator | Urgency Level |
|---|---|---|---|
| $\text{days} < 0$ | **Expired** | 🔴 Red Badge | Critical |
| $\text{days} = 0$ | **Expires Today** | 🟠 Orange Badge | Urgent |
| $1 \le \text{days} \le 3$ | **Expiring Soon** | 🟡 Yellow Badge | High Priority |
| $4 \le \text{days} \le 7$ | **Use Soon** | 🔵 Blue/Info Badge | Medium Priority |
| $\text{days} > 7$ | **Fresh** | 🟢 Green Badge | Fresh / Good |

---

## 🗄️ Database Design (Schema)

The database uses SQLite with 5 relational tables:

```
[ users ] (1)
    │
    ├──< [ pantry_items ] (N)
    │         │
    │         └──< [ food_waste ] (N)
    │
    └──< [ food_waste ] (N)

[ recipes ] (1) ──< [ recipe_ingredients ] (N)
```

1. **`users`**:
   - `id` (PK, Integer)
   - `name` (String 100)
   - `email` (String 120, Unique)
   - `password_hash` (String 200)
   - `created_at` (DateTime)

2. **`pantry_items`**:
   - `id` (PK, Integer)
   - `user_id` (FK -> users.id)
   - `name` (String 100)
   - `category` (String 50)
   - `quantity` (Float)
   - `unit` (String 20)
   - `purchase_date` (Date)
   - `expiry_date` (Date)
   - `status` (String 20: 'available', 'consumed', 'wasted')
   - `created_at` (DateTime)

3. **`recipes`**:
   - `id` (PK, Integer)
   - `name` (String 150)
   - `description` (Text)
   - `instructions` (Text)
   - `cooking_time` (Integer minutes)
   - `difficulty` (String 20: Easy, Medium, Hard)
   - `dietary_type` (String 50: Vegetarian, Non-Vegetarian, Vegan)
   - `created_at` (DateTime)

4. **`recipe_ingredients`**:
   - `id` (PK, Integer)
   - `recipe_id` (FK -> recipes.id)
   - `ingredient_name` (String 100)
   - `quantity` (String 50)
   - `unit` (String 50)

5. **`food_waste`**:
   - `id` (PK, Integer)
   - `user_id` (FK -> users.id)
   - `pantry_item_id` (FK -> pantry_items.id, Nullable)
   - `item_name` (String 100)
   - `quantity` (Float)
   - `unit` (String 20)
   - `reason` (String 50: Expired, Spoiled, Over-purchased, Not used, Other)
   - `waste_date` (Date)

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.8+ installed on your operating system.
- Terminal / PowerShell access.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
Seeds 32 Indian and International recipes, a demo user, and realistic expiring pantry demo items:
```bash
python seed/seed_data.py
```

### 4. Run the Web Server
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Credentials
> ⚠️ **Notice**: For local testing and examination demonstration only. Change passwords for production deployment.

- **Email**: `demo@smartpantry.local`
- **Password**: `Demo@123`

---

## 🧪 Automated Testing
Run the comprehensive test suite verifying authentication, expiry calculations, recommendation scoring, pantry deductions, and waste logging:
```bash
python test_system.py
```

---

## 🌐 Implemented Application Routes

| Method | Endpoint | Description |
|---|---|---|
| `GET, POST` | `/register` | User account registration |
| `GET, POST` | `/login` | User login and session initiation |
| `GET` | `/logout` | Terminate session and logout |
| `GET` | `/` or `/dashboard` | Main user dashboard with stats and alerts |
| `GET` | `/pantry` | Full pantry inventory with search/filter/sort |
| `GET, POST` | `/pantry/add` | Add new food item to pantry |
| `GET, POST` | `/pantry/edit/<id>` | Edit existing food item |
| `POST` | `/pantry/delete/<id>` | Remove item from pantry |
| `POST` | `/pantry/used/<id>` | Mark item as consumed/used |
| `GET, POST` | `/pantry/wasted/<id>` | Mark pantry item as wasted with reason |
| `GET` | `/expiring` | Expiring soon alerts categorized by urgency |
| `GET` | `/recipes` | Filterable recipe catalog with dynamic match scores |
| `GET` | `/recipes/<id>` | Recipe detail page with matched/missing ingredients |
| `POST` | `/recipes/<id>/use` | Cook recipe and deduct ingredients from pantry |
| `GET` | `/waste` | Food waste log and tracking table |
| `POST` | `/waste/add` | Manually record food waste |
| `POST` | `/waste/delete/<id>` | Delete food waste entry |
| `GET` | `/analytics` | Interactive Chart.js analytics & environmental impact |
| `GET` | `/ai-assistant` | 🤖 Smart Pantry AI chat interface with quick prompts |
| `POST` | `/api/ai/chat` | AJAX API endpoint for conversational AI recipe queries |
| `GET` | `/api/ai/recommend` | AJAX API endpoint for AI-ranked recipe suggestions |
| `GET` | `/api/ai/pantry-context` | AJAX endpoint returning structured, privacy-safe pantry context |

---

## 🧪 Automated Testing

Run the full automated test suite verifying core workflows and AI capabilities:
```bash
# 1. Test Core System (Auth, Pantry CRUD, Expiry Math, Recipe Scoring, Waste Tracking)
python test_system.py

# 2. Test AI Layer (Privacy, Context Builder, Fallbacks, Substitutions, AI Chat API)
python test_ai.py
```

## 🔮 Future Scope
1. **Barcode / QR Code Scanning**: Quick grocery check-in using mobile camera.
2. **Receipt OCR Scanning**: Automatically extract food items from grocery receipts.
3. **Smart Refrigerator Integration**: IoT sensor integration to track freshness.
4. **AI Recipe Generation**: LLM-powered dynamic recipe creation using obscure ingredient combinations.
5. **Mobile Application**: Native Flutter or React Native client.

---

## ⚠️ Known Limitations
1. Expiry calculations rely on dates input by users at the time of purchase.
2. Recipe ingredients matching utilizes fuzzy string inclusion which handles typical plurals and prefixes, but complex culinary synonyms require explicit aliases.

---

## 🤝 CEP Social Impact Statement
Smart Pantry directly addresses **United Nations Sustainable Development Goal 12.3** (*Halve per capita global food waste at the retail and consumer levels by 2030*). By transforming domestic kitchens into conscious, expiry-aware spaces, users conserve financial resources while mitigating the methane emissions and ecological strain associated with rotting municipal landfill waste.
