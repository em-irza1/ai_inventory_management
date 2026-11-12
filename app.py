import os
import logging

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from inventory import InventoryManager
from ai_helper import InventoryAI


# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)

app.config["JSON_SORT_KEYS"] = False

logging.basicConfig(level=logging.INFO)

DATA_FILE = os.path.join(BASE_DIR, "data", "products.json")


# ==========================================
# INITIALIZE CLASSES
# ==========================================

inventory = InventoryManager(DATA_FILE)

ai = InventoryAI()


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# PRODUCT MANAGEMENT
# ==========================================

@app.route("/api/products", methods=["GET"])
def get_products():

    query = request.args.get("q", "").strip()

    if query:
        products = inventory.search_products(query)
    else:
        products = inventory.get_all_products()

    return jsonify({
        "success": True,
        "products": products,
        "stats": inventory.get_statistics()
    })


@app.route("/api/products", methods=["POST"])
def add_product():

    data = request.get_json(silent=True) or {}

    try:

        product = inventory.add_product(data)

        return jsonify({
            "success": True,
            "message": "Product added successfully.",
            "product": product
        }), 201

    except ValueError as exc:

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400


@app.route("/api/products/<product_id>", methods=["PUT"])
def update_product(product_id):

    data = request.get_json(silent=True) or {}

    try:

        product = inventory.update_product(product_id, data)

        if not product:

            return jsonify({
                "success": False,
                "error": "Product not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Product updated successfully.",
            "product": product
        })

    except ValueError as exc:

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400


@app.route("/api/products/<product_id>", methods=["DELETE"])
def delete_product(product_id):

    deleted = inventory.delete_product(product_id)

    if not deleted:

        return jsonify({
            "success": False,
            "error": "Product not found."
        }), 404

    return jsonify({
        "success": True,
        "message": "Product deleted successfully."
    })


# ==========================================
# AI INVENTORY ANALYSIS
# ==========================================

@app.route("/api/ai/analyze", methods=["POST"])
def ai_analyze():

    products = inventory.get_all_products()

    return ai_response("analysis", products)


# ==========================================
# AI REORDER SUGGESTIONS
# ==========================================

@app.route("/api/ai/reorder", methods=["POST"])
def ai_reorder():

    products = inventory.get_all_products()

    return ai_response("reorder", products)


# ==========================================
# AI INVENTORY ASSISTANT
# ==========================================

@app.route("/api/ai/ask", methods=["POST"])
def ai_ask():

    data = request.get_json(silent=True) or {}

    question = str(data.get("question", "")).strip()

    if not question:

        return jsonify({
            "success": False,
            "error": "Please enter a question."
        }), 400

    products = inventory.get_all_products()

    return ai_response(
        "ask",
        products,
        question
    )


# ==========================================
# AI PRODUCT DESCRIPTION GENERATOR
# ==========================================

@app.route("/api/ai/description", methods=["POST"])
def ai_description():

    data = request.get_json(silent=True) or {}

    try:

        result = ai.generate_description(data)

        return jsonify({
            "success": True,
            "result": result
        })

    except ValueError as exc:

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except RuntimeError as exc:

        app.logger.exception("AI configuration error")

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 503

    except Exception as exc:

        app.logger.exception("AI description error")

        return jsonify({
            "success": False,
            "error": f"AI Error: {str(exc)}"
        }), 502


# ==========================================
# CENTRAL AI RESPONSE FUNCTION
# ==========================================

def ai_response(mode, products, question=None):

    try:

        result = ai.generate(
            mode,
            products,
            question
        )

        return jsonify({
            "success": True,
            "result": result
        }), 200

    except RuntimeError as exc:

        app.logger.exception(
            "AI configuration error"
        )

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 503

    except Exception as exc:

        app.logger.exception(
            "AI request failed: %s",
            str(exc)
        )

        return jsonify({
            "success": False,
            "error": f"AI Error: {str(exc)}"
        }), 502


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "application": "Stockwise",
        "ai_configured": ai.is_configured(),
        "model": ai.model
    })


# ==========================================
# ERROR HANDLING
# ==========================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "error": "Requested resource not found."
    }), 404


@app.errorhandler(500)
def internal_error(error):

    app.logger.exception("Internal server error")

    return jsonify({
        "success": False,
        "error": "An internal server error occurred."
    }), 500


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )