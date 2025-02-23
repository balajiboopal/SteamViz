from flask import Flask, jsonify, request, Blueprint
from src.modules import update
from dotenv import load_dotenv
import os

extract_bp = Blueprint("extraction", __name__, url_prefix="/update")
load_dotenv()


@extract_bp.route("/", methods=["GET"])
def extract():
    key = request.args.get("API_KEY")
    if key != os.getenv("API_KEY"):
        return jsonify({"status": "error", "message": "Invalid API Key!"}), 401
    result = update.update_database()
    return jsonify(result)
