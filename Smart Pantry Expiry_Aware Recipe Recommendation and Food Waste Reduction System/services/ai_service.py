"""
Smart Pantry AI Service
Provides AI-powered recipe recommendations, natural language recipe generation,
expiry-aware culinary reasoning, and intelligent ingredient substitutions.
"""

import os
import json
import re
import requests
from config import Config
from models.pantry import PantryItem
from models.recipe import Recipe

SYSTEM_PROMPT = """You are Smart Pantry AI.
Your job is to help users reduce food waste by suggesting recipes based on ingredients they already have.
Prioritize ingredients that are approaching expiry.
Never claim that an item is expired based on your own reasoning.
Use the expiry status supplied by the application.
Prefer recipes requiring ingredients already available to the user.
Clearly identify missing ingredients.
Do not invent pantry items.
Do not invent expiry dates.
Do not provide unsafe food advice.
Keep recommendations practical, appetizing, and easy to prepare."""


def build_pantry_context(pantry_items):
    """
    Builds a structured, privacy-safe representation of the user's pantry.
    Only food inventory and expiry metadata are included. Never personal info.
    """
    if not pantry_items:
        return {
            "items": [],
            "context_text": "Pantry is currently empty.",
            "expiring_soon": [],
            "expired": [],
            "fresh": []
        }

    items_data = []
    text_lines = []
    expiring_soon = []
    expired = []
    fresh = []

    for item in pantry_items:
        # Expiry calculation comes strictly from the existing model/backend logic
        days = item.days_remaining
        status = item.computed_status

        entry = {
            "name": item.name,
            "category": item.category,
            "quantity": f"{item.quantity} {item.unit}",
            "purchase_date": str(item.purchase_date) if item.purchase_date else "N/A",
            "expiry_date": str(item.expiry_date) if item.expiry_date else "N/A",
            "days_remaining": days,
            "status": status
        }
        items_data.append(entry)

        # Formatted line for LLM context
        line = (f"- Food: {item.name} | Quantity: {item.quantity} {item.unit} | "
                f"Expiry: {item.expiry_date} | Days remaining: {days} | Status: {status}")
        text_lines.append(line)

        if status in ['Expiring Soon', 'Expires Today']:
            expiring_soon.append(item.name)
        elif status == 'Expired':
            expired.append(item.name)
        else:
            fresh.append(item.name)

    context_text = (
        "USER'S CURRENT PANTRY INVENTORY:\n" +
        "\n".join(text_lines) +
        f"\n\nExpiring Soon ({len(expiring_soon)} items): {', '.join(expiring_soon) if expiring_soon else 'None'}"
        f"\nExpired ({len(expired)} items): {', '.join(expired) if expired else 'None'}"
        f"\nFresh / Safe ({len(fresh)} items): {', '.join(fresh) if fresh else 'None'}"
    )

    return {
        "items": items_data,
        "context_text": context_text,
        "expiring_soon": expiring_soon,
        "expired": expired,
        "fresh": fresh
    }


def _extract_json(text):
    """Safely extracts JSON from an LLM response string."""
    if not text:
        return None
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try extracting between ```json ... ``` codeblocks
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except Exception:
            pass

    # Try finding outermost { ... }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(text[first_brace:last_brace + 1])
        except Exception:
            pass

    return None


def call_ai_model(prompt, system_instruction=SYSTEM_PROMPT, response_json=True):
    """
    Provider abstraction for AI calls.
    Supports Google Gemini via google-genai SDK, fallback REST API, and graceful failure.
    """
    api_key = Config.AI_API_KEY
    model = Config.AI_MODEL or 'gemini-2.5-flash'
    provider = (Config.AI_PROVIDER or 'gemini').lower()

    if not api_key or api_key == 'your_api_key_here':
        return {
            "success": False,
            "error_type": "missing_api_key",
            "message": "Smart Pantry AI is temporarily unavailable. You can still use the normal recipe recommendation system.",
            "data": None
        }

    # Attempt 1: Using official google-genai SDK
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2 if response_json else 0.4
        )
        if response_json:
            config.response_mime_type = "application/json"

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )

        output_text = response.text if hasattr(response, 'text') else str(response)
        if response_json:
            parsed = _extract_json(output_text)
            if parsed is not None:
                return {"success": True, "data": parsed, "raw_text": output_text}
            # Fallback to returning raw text if JSON parsing fails
            return {"success": True, "data": None, "raw_text": output_text}
        return {"success": True, "data": None, "raw_text": output_text}

    except Exception as sdk_err:
        # Check if it was a rate limit / auth / network error
        err_str = str(sdk_err)

    # Attempt 2: Fallback via direct Gemini REST API
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": 0.2 if response_json else 0.4
            }
        }
        if response_json:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        res = requests.post(url, headers=headers, json=payload, timeout=12)
        if res.status_code == 200:
            res_data = res.json()
            candidates = res_data.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts:
                    raw_text = parts[0].get('text', '')
                    if response_json:
                        parsed = _extract_json(raw_text)
                        return {"success": True, "data": parsed, "raw_text": raw_text}
                    return {"success": True, "data": None, "raw_text": raw_text}

        return {
            "success": False,
            "error_type": "api_error",
            "message": "Smart Pantry AI is temporarily unavailable. You can still use the normal recipe recommendation system.",
            "data": None
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_type": "timeout",
            "message": "The AI request timed out. Please try again or use the standard recipe recommendation.",
            "data": None
        }
    except Exception as rest_err:
        return {
            "success": False,
            "error_type": "network_error",
            "message": "Smart Pantry AI is temporarily unavailable. You can still use the normal recipe recommendation system.",
            "data": None
        }


def get_ai_recipe_recommendations(pantry_items, limit=3):
    """
    Generates AI-powered recipe recommendations taking into account available items,
    expiry urgency, and cooking practicality.
    """
    if not pantry_items:
        return {
            "success": False,
            "message": "Your pantry is empty. Add items to your pantry to get AI recommendations!",
            "recommendations": []
        }

    context = build_pantry_context(pantry_items)
    prompt = f"""Based on the user's pantry below, suggest up to {limit} creative recipes that prioritize using ingredients expiring soon.
Never suggest using items with status 'Expired'.

{context['context_text']}

Respond with a JSON object in this exact format:
{{
  "recommendations": [
    {{
      "recipe_name": "Recipe Name",
      "reason": "Why this recipe helps reduce food waste (mention specific expiring ingredients)",
      "cooking_time": "15 minutes",
      "difficulty": "Easy",
      "available_ingredients": ["Item 1", "Item 2"],
      "missing_ingredients": ["Item 3 (optional)"],
      "steps": [
        "Step 1...",
        "Step 2..."
      ]
    }}
  ]
}}
"""
    result = call_ai_model(prompt, response_json=True)
    if result["success"] and result["data"] and "recommendations" in result["data"]:
        return {
            "success": True,
            "recommendations": result["data"]["recommendations"],
            "message": "AI recommendations generated successfully."
        }

    # If AI service is unavailable, provide a fallback recommendation using local database
    fallback = _local_rule_based_recommendation(pantry_items, limit=limit)
    return {
        "success": False,
        "message": result.get("message") or "Smart Pantry AI is temporarily unavailable. You can still use the normal recipe recommendation system.",
        "recommendations": fallback
    }


def generate_recipe(user_prompt, pantry_items):
    """
    Generates a custom recipe based on a user's natural language request and current pantry.
    """
    context = build_pantry_context(pantry_items)
    prompt = f"""The user asks: "{user_prompt}"

Here is the user's current pantry inventory:
{context['context_text']}

Generate a single delicious, practical recipe that satisfies the user's request while prioritizing items close to expiry.
If the recipe requires an ingredient the user is missing, clearly list it and mention a safe substitute if possible.

Respond with a JSON object in this exact schema:
{{
  "recipe_name": "Tomato Egg Toast",
  "reason": "Uses bread that expires tomorrow",
  "cooking_time": "10 minutes",
  "difficulty": "Easy",
  "available_ingredients": ["Bread", "Tomato", "Egg"],
  "missing_ingredients": [],
  "substitutions": [
    {{"missing": "Cheese", "substitute": "None needed / pinch of herbs", "note": "Can be skipped"}}
  ],
  "steps": [
    "Toast the bread",
    "Prepare the tomato mixture",
    "Cook the egg",
    "Assemble and serve"
  ]
}}
"""
    result = call_ai_model(prompt, response_json=True)
    if result["success"] and result["data"] and "recipe_name" in result["data"]:
        return {"success": True, "recipe": result["data"]}

    if result.get("raw_text"):
        return {
            "success": True,
            "recipe": None,
            "text_response": result["raw_text"]
        }

    return {
        "success": False,
        "message": result.get("message", "Could not generate recipe."),
        "recipe": None
    }


def suggest_ingredient_substitutions(recipe_name, missing_ingredients, pantry_items):
    """
    Suggests safe, practical culinary substitutes for missing ingredients using pantry items.
    """
    context = build_pantry_context(pantry_items)
    prompt = f"""A user wants to make "{recipe_name}".
They are missing these ingredients: {', '.join(missing_ingredients) if isinstance(missing_ingredients, list) else missing_ingredients}.

Here are the ingredients they currently have available:
{context['context_text']}

Suggest practical and safe culinary alternatives from their pantry or explain if the missing ingredient can simply be omitted.
Do not claim that an unsafe or unsuitable substitution is equivalent.

Respond in JSON:
{{
  "substitutions": [
    {{
      "missing": "Name of missing item",
      "suggested_substitute": "Available item from pantry or 'Omit'",
      "explanation": "Why this works or how to adjust the recipe"
    }}
  ]
}}
"""
    result = call_ai_model(prompt, response_json=True)
    if result["success"] and result["data"] and "substitutions" in result["data"]:
        return result["data"]["substitutions"]
    return []


def ask_pantry_ai(user_message, pantry_items):
    """
    Main conversational handler for the 'Ask Smart Pantry AI' chat interface.
    Understands expiry questions, recipe requests, ingredient queries, and substitutions.
    Returns structured recipe card when recipe is generated, or conversational advice.
    """
    clean_message = (user_message or "").strip()
    if not clean_message:
        return {
            "success": False,
            "message": "Please enter a question or recipe request.",
            "structured_recipe": None
        }

    context = build_pantry_context(pantry_items)
    pantry_count = len(pantry_items) if pantry_items else 0
    expiring_count = len(context["expiring_soon"])

    prompt = f"""User message: "{clean_message}"

{context['context_text']}

Instructions:
1. If the user is asking what to cook, requesting a recipe, or asking to use specific ingredients, provide a full recipe in the "recipe" field AND a brief conversational response in "reply".
2. If the user asks a general pantry question (e.g. "What expires soon?", "How many items do I have?"), answer it accurately in the "reply" field using the inventory data above, and set "recipe" to null.
3. Prioritize items expiring soon. Never state that an item is expired unless its Status above says 'Expired'.
4. Clearly distinguish available pantry ingredients from missing ingredients.
5. If ingredients are missing, include sensible substitutions where appropriate.

Format your response as valid JSON with this structure:
{{
  "reply": "Friendly conversational summary or answer...",
  "has_recipe": true,
  "recipe": {{
    "recipe_name": "Tomato Egg Toast",
    "reason": "Uses bread that expires tomorrow and tomatoes",
    "cooking_time": "10 minutes",
    "difficulty": "Easy",
    "available_ingredients": ["Bread", "Tomato", "Egg"],
    "missing_ingredients": [],
    "substitutions": [],
    "steps": [
      "Toast the bread",
      "Cook the eggs and tomatoes",
      "Assemble and serve"
    ]
  }}
}}
"""
    result = call_ai_model(prompt, response_json=True)

    if result["success"]:
        data = result.get("data")
        if data and isinstance(data, dict):
            reply = data.get("reply", "")
            recipe = data.get("recipe")
            has_recipe = bool(data.get("has_recipe") and recipe)
            return {
                "success": True,
                "message": reply or "Here is what I recommend based on your pantry:",
                "has_recipe": has_recipe,
                "structured_recipe": recipe if has_recipe else None,
                "pantry_count": pantry_count,
                "expiring_count": expiring_count
            }
        elif result.get("raw_text"):
            # Graceful fallback to text if JSON wasn't parsed
            return {
                "success": True,
                "message": result["raw_text"],
                "has_recipe": False,
                "structured_recipe": None,
                "pantry_count": pantry_count,
                "expiring_count": expiring_count
            }

    # Error handling & intelligent local fallback
    fallback_message = result.get("message") or "Smart Pantry AI is temporarily unavailable. You can still use the normal recipe recommendation system."
    fallback_recipes = _local_rule_based_recommendation(pantry_items, limit=1)

    structured_fallback = None
    if fallback_recipes:
        rec = fallback_recipes[0]
        structured_fallback = {
            "recipe_name": rec.get("recipe_name"),
            "reason": rec.get("reason"),
            "cooking_time": rec.get("cooking_time", "20 minutes"),
            "difficulty": rec.get("difficulty", "Easy"),
            "available_ingredients": rec.get("available_ingredients", []),
            "missing_ingredients": rec.get("missing_ingredients", []),
            "substitutions": [],
            "steps": rec.get("steps", ["Follow standard recipe cooking steps."])
        }

    return {
        "success": False,
        "is_fallback": True,
        "message": fallback_message,
        "has_recipe": bool(structured_fallback),
        "structured_recipe": structured_fallback,
        "pantry_count": pantry_count,
        "expiring_count": expiring_count
    }


def _local_rule_based_recommendation(pantry_items, limit=3):
    """
    Deterministic rule-based fallback using existing database recipes.
    Runs when the external AI API is unavailable, ensuring zero downtime for users.
    """
    from services.recommendation_service import calculate_match
    if not pantry_items:
        return []

    try:
        all_recipes = Recipe.query.all()
    except Exception:
        return []

    scored = []
    for recipe in all_recipes:
        match_info = calculate_match(recipe, pantry_items)
        if match_info['match_count'] > 0:
            expiring_names = [item.name for item in match_info['expiring_matches']]
            reason = ("Prioritizes expiring items: " + ", ".join(expiring_names)) if expiring_names else "Uses available pantry ingredients"
            scored.append({
                "recipe_name": recipe.name,
                "reason": reason,
                "cooking_time": f"{recipe.cooking_time} minutes",
                "difficulty": recipe.difficulty,
                "available_ingredients": [item.name for item in match_info['matched_items']],
                "missing_ingredients": [
                    ing.ingredient_name for ing in recipe.ingredients
                    if not any(ing.ingredient_name.lower() in p.name.lower() or p.name.lower() in ing.ingredient_name.lower() for p in pantry_items)
                ],
                "steps": [s.strip() for s in recipe.instructions.split("\n") if s.strip()],
                "score": match_info['final_score']
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]
