#!/usr/bin/env python3

from flask import Flask, request, make_response,jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route("/heroes", methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([{
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name
    } for hero in heroes])



@app.route("/heroes/<int:id>", methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero:
        hero_dict = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "hero_powers": [
                {
                    "hero_id": hero_power.hero_id,
                    "id": hero_power.id,
                    "power": {
                        "id": hero_power.power.id,
                        "name": hero_power.power.name,
                        "description": hero_power.power.description
                    },
                    "power_id": hero_power.power_id,
                    "strength": hero_power.strength
                }
                for hero_power in hero.hero_powers
            ]
        }
        return jsonify(hero_dict)
    else:
        return jsonify({"error": "Hero not found"}), 404

@app.route("/powers",methods=['GET'])
def get_powers():
    get_powers=Power.query.all()
    get_powers=[power.to_dict() for power in get_powers]
    return get_powers

@app.route("/powers/<int:id>",methods=['GET'])
def get_power(id):
    get_power=Power.query.filter_by(id=id).first()
    if not get_power:
        return{"error": "Power not found"},404
    return get_power.to_dict(),200





@app.route("/powers/<int:id>", methods=['PATCH'])
def update_power(id):
    power = Power.query.filter_by(id=id).first()

    if not power:
        return {"error": "Power not found"}, 404

    data = request.get_json()

    # Update the description field if it's in the request data
    if 'description' in data:
        power.description = data['description']
        
        # Validate that the description is at least 20 characters
        if not isinstance(power.description, str) and len(power.description) < 20:
            return {"errors": ["Description must be at least 20 characters"]}, 400

    # Validate and update if there is any other valid field
    if 'name' in data:
        power.name = data['name']

    try:
        # Assuming `validate` checks the power's attributes for validation
        power.validate()
        db.session.commit()

        # Return the updated power's dictionary representation
        return power.to_dict(), 200

    except Exception:
        # Return the specified error message for validation failure
        return {"errors": ["validation errors"]}, 400










@app.route("/hero_powers", methods=['POST'])
def create_hero_power():
    data = request.get_json()

    # Validate that required fields are present
    strength = data.get('strength')
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')

    # Check if strength, hero_id, and power_id are provided
    if not all([strength, hero_id, power_id]):
        return {"error": "strength, hero_id, and power_id are required"}, 400

    # Validate strength value
    allowed_strengths = {"Strong", "Weak", "Average"}
    if strength not in allowed_strengths:
        return {"error": "Strength must be one of: Strong, Weak, Average"}, 400

    # Fetch the Hero and Power objects to validate their existence
    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)

    if not hero:
        return {"error": "Hero not found"}, 404  # Hero does not exist

    if not power:
        return {"error": "Power not found"}, 404  # Power does not exist

    # Create new HeroPower object
    new_hero_power = HeroPower(
        strength=strength,
        hero_id=hero_id,
        power_id=power_id
    )

    try:
        db.session.add(new_hero_power)
        db.session.commit()
        return new_hero_power.to_dict(), 200  # Ensure we return 201 status code
    except Exception as e:
        db.session.rollback()  # Rollback if there's an error
        return {" errors": "validation errors"}, 500








if __name__ == '__main__':
    app.run(port=5555, debug=True)
