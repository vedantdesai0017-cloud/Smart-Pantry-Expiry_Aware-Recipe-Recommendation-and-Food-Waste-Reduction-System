# Project Documentation: Smart Pantry - Expiry-Aware Recipe Recommendation and Food Waste Reduction System

## 1. Abstract
Household food waste is a massive global issue, driven largely by forgotten pantry inventory and expiring ingredients. The "Smart Pantry" system is a web-based application developed to combat this problem. It allows users to manage their grocery inventory, track expiry dates, and intelligently recommends recipes based on ingredients that are nearing expiration. By prioritizing at-risk ingredients, the system actively helps households minimize waste, save money, and contribute to environmental sustainability.

## 2. Introduction
In our fast-paced modern lives, keeping track of groceries often falls by the wayside. Food items are frequently pushed to the back of the fridge or pantry, only to be discovered long after they have spoiled. The Smart Pantry application provides a centralized platform to log groceries alongside their expiration dates. It goes beyond simple tracking by proactively suggesting culinary solutions (recipes) to utilize items before they go bad.

## 3. Problem Statement
Annually, millions of tons of edible food are discarded by households simply because consumers forget what they have or miss expiration dates. Current inventory management methods are either manual (pen and paper) or basic tracking apps that lack actionable solutions. There is a need for an intelligent system that not only tracks inventory but provides immediate, actionable recommendations to utilize expiring food.

## 4. Objectives
- To develop a secure, user-friendly web application for managing household grocery inventory.
- To implement an automated expiry tracking system that categorizes items by urgency.
- To design a smart recipe recommendation algorithm that prioritizes ingredients nearing expiration.
- To provide a dashboard for users to track their food waste over time, encouraging better purchasing habits.

## 5. Existing Systems
Existing systems in the market primarily focus on either pure inventory tracking (like basic pantry apps) or recipe discovery (like standard cooking blogs/apps).
- **Inventory Apps:** Require high manual effort and only send passive push notifications without offering solutions on *how* to use the expiring items.
- **Recipe Apps:** Allow searching by ingredient but do not account for the urgency of an ingredient's expiry.

## 6. Proposed System
The proposed "Smart Pantry" system bridges the gap between inventory tracking, recipe discovery, and generative artificial intelligence. It integrates real-time inventory management with an expiry-aware recommendation engine and a dedicated **Smart Pantry AI Assistant**. The core innovations include:
1. Dynamic shelf-life evaluation based on mathematical remaining days without AI hallucination.
2. A hybrid recommendation engine pairing deterministic scoring with generative AI reasoning.
3. Natural language query processing via Google Gemini for custom recipe creation and culinary ingredient substitutions.
4. Privacy-preserving context extraction sending only sanitized inventory items to the LLM.

## 7. Scope
The scope of this project encompasses:
- Web-based user authentication and profile management.
- CRUD operations for pantry items and food waste logs.
- A seeded database of 30+ diverse recipes (Indian and International).
- A dynamic matching algorithm.
- *Out of scope:* Mobile application, automatic receipt scanning, and external supermarket API integrations (reserved for future scope).

## 8. Literature/Background Study
- **[REFERENCE PLACEHOLDER 1]**: Studies on domestic food waste indicate that over 30% of household food purchases end up in the bin, primarily due to poor inventory visibility.
- **[REFERENCE PLACEHOLDER 2]**: Research on consumer behavior shows that providing immediate, actionable solutions (like recipes) drastically reduces the likelihood of an item being wasted compared to passive alerts.

## 9. Methodology
The project follows an Agile development methodology.
1. **Requirement Gathering:** Defining functional and non-functional requirements.
2. **Design:** Creating ER diagrams, DFDs, and UI wireframes.
3. **Development:** Implementing the backend (Flask/SQLite) and frontend (HTML/CSS/Bootstrap).
4. **Testing:** Unit testing for the recommendation algorithm and integration testing for web routes.
5. **Deployment:** Setting up the local environment and seeding database scripts.

## 10. System Requirements
- OS: Windows 10/11, macOS, or Linux
- Web Browser: Google Chrome, Firefox, Safari, or Edge
- Internet connection (for fetching external CSS/JS libraries like Bootstrap, if used via CDN)

## 11. Hardware Requirements
- Processor: Intel Core i3 or equivalent (minimum)
- RAM: 4 GB (minimum)
- Storage: 500 MB free space for application files and database

## 12. Software Requirements
- Python 3.8 or higher
- Flask 3.0.3, Flask-SQLAlchemy 3.1.1
- SQLite3 (built into Python)
- IDE/Text Editor (e.g., VS Code)

## 13. Functional Requirements
- **User Module:** Secure registration, login, and logout.
- **Inventory Module:** Add, update, delete, and view pantry items with associated expiry dates.
- **Recommendation Module:** Algorithmically suggest recipes based on pantry items, sorted by expiry urgency.
- **Waste Tracking Module:** Log discarded items to track monetary and physical waste over time.

## 14. Non-functional Requirements
- **Performance:** Recipe recommendations must generate in under 2 seconds.
- **Usability:** The interface must be intuitive, requiring minimal clicks to add an item.
- **Security:** Passwords must be hashed (using Werkzeug). User data must be isolated.
- **Reliability:** The SQLite database must safely persist data across application restarts.

## 15. System Architecture
The application uses a Model-View-Controller (MVC) architecture pattern (adapted for Flask):
- **Model:** SQLAlchemy classes defining the database schema (User, PantryItem, Recipe, etc.).
- **View:** Jinja2 HTML templates rendering the UI.
- **Controller:** Flask route functions handling HTTP requests, business logic, and algorithm execution.

## 16. Use Case Description
- **Use Case 1: Add Pantry Item:** User enters item name, category, quantity, and expiry date. System validates and saves to DB.
- **Use Case 2: Get Recommendations:** User navigates to recipes. System fetches user's pantry items, identifies expiring items, calculates match scores against the Recipe database, and displays top matches.
- **Use Case 3: Log Waste:** User discards an item, logs it in the waste tracker with a reason (e.g., "Spoiled"). System updates waste metrics.

## 17. ER Diagram Description
The Entity-Relationship architecture consists of:
- **User** (1) to (N) **PantryItem**
- **User** (1) to (N) **FoodWaste**
- **Recipe** (1) to (N) **RecipeIngredient**
The Recommendation Engine acts as an associative process querying PantryItem and RecipeIngredient.

## 18. DFD Level 0 Description
**Context Diagram:**
- The **User** interacts with the **Smart Pantry System**.
- The User inputs: Registration details, Pantry Items, Waste Logs.
- The System outputs: Inventory Dashboard, Expiry Alerts, Recipe Recommendations, Waste Statistics.

## 19. DFD Level 1 Description
Decomposing Level 0:
- **Process 1.0 (Auth):** Handles user credentials and sessions.
- **Process 2.0 (Inventory Management):** Reads/writes to the Pantry database based on user CRUD inputs.
- **Process 3.0 (Recommendation Engine):** Pulls data from Pantry DB and Recipe DB, processes the matching algorithm, and outputs a sorted list to the user.
- **Process 4.0 (Waste Tracking):** Logs discarded data to the Waste DB.

## 20. Database Design
**Table 1: User**
- `id` (PK), `name` (String), `email` (String, Unique), `password_hash` (String), `created_at` (DateTime)

**Table 2: PantryItem**
- `id` (PK), `user_id` (FK), `name` (String), `category` (String), `quantity` (Float), `unit` (String), `expiry_date` (Date)

**Table 3: Recipe**
- `id` (PK), `name` (String), `description` (String), `instructions` (Text), `cooking_time` (Integer), `difficulty` (String), `dietary_type` (String)

**Table 4: RecipeIngredient**
- `id` (PK), `recipe_id` (FK), `ingredient_name` (String), `quantity` (String), `unit` (String)

**Table 5: FoodWaste**
- `id` (PK), `user_id` (FK), `item_name` (String), `quantity` (Float), `unit` (String), `waste_date` (Date), `reason` (String)

## 21. Algorithm
**Smart Recommendation Algorithm Formulation:**

The scoring formula integrates three key metrics:
$$\text{Final Score} = (\text{Ingredient Match} \times 0.60) + (\text{Expiry Priority} \times 0.30) + (\text{Availability Bonus} \times 0.10)$$

Where:
- **Ingredient Match (0.0 to 1.0):**
  $$\text{Match Ratio} = \frac{\text{Number of Matched Pantry Ingredients}}{\text{Total Recipe Ingredients}}$$
- **Expiry Priority (0.0 to 1.0):**
  Evaluates the urgency of the matched ingredients:
  - Expired / Expires Today ($\le 0$ days remaining): Weight = $1.00$
  - High Priority ($1 \le \text{days} \le 3$): Weight = $0.85$
  - Medium Priority ($4 \le \text{days} \le 7$): Weight = $0.60$
  - Fresh / Stable ($> 7$ days): Weight = $0.20$
  $$\text{Expiry Score} = \frac{\sum \text{Weights of Matched Ingredients}}{\text{Total Recipe Ingredients}}$$
- **Availability Bonus (0.0 to 1.0):**
  $1.0$ if $\text{Match Ratio} \ge 0.50$, else $\text{Match Ratio} \times 2.0$.
- **Final Normalized Score (0 to 100):**
  $$\text{Score} = \text{round}(\text{Final Score} \times 100)$$

**Pseudocode:**
```text
FUNCTION CalculateRecommendationScore(recipe, pantry_items):
    matched_ingredients = []
    expiring_matches = []
    total_recipe_ingredients = LENGTH(recipe.ingredients)

    FOR EACH req_ingredient IN recipe.ingredients:
        FOR EACH p_item IN pantry_items:
            IF req_ingredient.name IN p_item.name OR p_item.name IN req_ingredient.name:
                matched_ingredients.APPEND(p_item)
                IF p_item.computed_status IN ['Expired', 'Expires Today', 'Expiring Soon']:
                    expiring_matches.APPEND(p_item)
                BREAK

    match_count = LENGTH(matched_ingredients)
    match_pct = match_count / total_recipe_ingredients

    expiry_priority_sum = 0
    FOR EACH item IN matched_ingredients:
        IF item.days_remaining <= 0:
            expiry_priority_sum += 1.00
        ELSE IF item.days_remaining <= 3:
            expiry_priority_sum += 0.85
        ELSE IF item.days_remaining <= 7:
            expiry_priority_sum += 0.60
        ELSE:
            expiry_priority_sum += 0.20

    expiry_priority = expiry_priority_sum / total_recipe_ingredients
    availability = 1.0 IF match_pct >= 0.5 ELSE match_pct * 2.0

    raw_score = (match_pct * 0.60) + (expiry_priority * 0.30) + (availability * 0.10)
    final_score = CLAMP(ROUND(raw_score * 100), 0, 100)

    RETURN {
        'match_count': match_count,
        'total': total_recipe_ingredients,
        'match_pct': match_pct,
        'expiry_score': expiry_priority,
        'final_score': final_score,
        'expiring_matches': expiring_matches
    }
```

## 22. Implementation Notes
- Utilized Flask's application context for database seeding.
- Implemented soft matching (case-insensitive string matching) for ingredient mapping between pantry items and recipes.
- Used Bootstrap for rapid, responsive UI development.

## 23. Testing
| Test ID | Module | Description | Expected Result | Status |
|---|---|---|---|---|
| TC01 | Auth | Login with valid demo credentials | Redirects to Dashboard | Pass |
| TC02 | Auth | Login with invalid password | Shows error message | Pass |
| TC03 | Pantry | Add item with past expiry date | System rejects/warns | Pass |
| TC04 | Recipe | Check recommendations with expiring Milk | Recipes containing Milk appear at top | Pass |
| TC05 | Waste | Log 1kg of spoiled rice | Dashboard shows waste incremented | Pass |

## 24. Results
The system successfully registers users and allows seamless tracking of pantry items. The recommendation algorithm effectively surfaces recipes that utilize ingredients within 3 days of expiration, dynamically altering the UI to highlight urgent cooking needs. The seed script successfully populates 32 diverse recipes to demonstrate system capability immediately.

## 25. Advantages
- **Proactive rather than reactive:** Actually tells users *what* to make with their expiring food.
- **Cost Saving:** Reduces household grocery bills by maximizing food utilization.
- **User Friendly:** Simple interface requiring minimal technical knowledge.
- **Lightweight:** SQLite and Flask make the application easy to host and run locally.

## 26. Limitations
- Relies heavily on the user manually inputting correct expiry dates and updating inventory after cooking.
- The recipe database is currently static; it does not dynamically scrape new recipes from the web.
- Lacks a mobile-native version for on-the-go supermarket logging.

## 27. Future Scope
- **Barcode/Receipt Scanner:** Integrate OCR to automatically parse supermarket receipts and populate the pantry.
- **API Integration:** Connect with external recipe APIs (like Spoonacular) for an infinite recipe database.
- **Push Notifications:** Send SMS or Email alerts for items expiring the next day.
- **Community Sharing:** Allow users to flag surplus non-perishables for local donation.

## 28. Social Impact
By targeting household food waste, this project addresses a critical node in the food supply chain. Reducing domestic food waste lowers greenhouse gas emissions from landfills and promotes sustainable consumption patterns, aligning perfectly with global sustainability goals.

## 29. Conclusion
The Smart Pantry system successfully demonstrates how technology can intervene in daily household management to promote sustainability. By combining simple inventory tracking with intelligent, expiry-aware recipe recommendations, the application provides a practical, easy-to-use solution to the widespread problem of domestic food waste.

## 30. References
1. [REFERENCE PLACEHOLDER] UN Environment Programme. (2021). Food Waste Index Report 2021.
2. [REFERENCE PLACEHOLDER] Quested, T. E., et al. (2013). "Spaghetti soup: The complex world of food waste behaviours." Resources, Conservation and Recycling.
3. [REFERENCE PLACEHOLDER] Flask Documentation: https://flask.palletsprojects.com/
4. [REFERENCE PLACEHOLDER] SQLAlchemy Documentation: https://www.sqlalchemy.org/
