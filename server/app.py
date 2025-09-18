#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource, abort

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = True

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):
    def get(self):
        plants = Plant.query.all()
        return [p.to_dict() for p in plants], 200

    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "JSON body required"}, 400

        name = data.get('name')
        image = data.get('image')
        price = data.get('price')
        missing = [field for field in ['name','image','price'] if data.get(field) is None]
        if missing:
            return {"error": f"Missing field(s): {', '.join(missing)}"}, 400

        new_plant = Plant(name=name, image=image, price=price)
        db.session.add(new_plant)
        db.session.commit()

        return new_plant.to_dict(), 201

class PlantByID(Resource):
    def get(self, plant_id):
        plant = Plant.query.get(plant_id)
        if not plant:
            abort(404, message=f"Plant with id {plant_id} not found")
        return plant.to_dict(), 200

    def patch(self, plant_id):
        """Update a plant partially (only fields provided)."""
        plant = Plant.query.get(plant_id)
        if not plant:
            abort(404, message=f"Plant with id {plant_id} not found")

        data = request.get_json()
        if not data:
            return {"error": "JSON body required"}, 400

        # Only update the fields that are in the request body
        # Allowed fields might include: name, image, price, is_in_stock (if your model has that)
        # Suppose you have `is_in_stock` column in your model

        if 'name' in data:
            plant.name = data['name']
        if 'image' in data:
            plant.image = data['image']
        if 'price' in data:
            plant.price = data['price']
        if 'is_in_stock' in data:
            plant.is_in_stock = data['is_in_stock']

        db.session.add(plant)
        db.session.commit()
        return plant.to_dict(), 200

    def delete(self, plant_id):
        """Delete a plant and return no content, status 204."""
        plant = Plant.query.get(plant_id)
        if not plant:
            abort(404, message=f"Plant with id {plant_id} not found")

        db.session.delete(plant)
        db.session.commit()
        # Return empty body with status code 204
        return "", 204

# Register resources
api.add_resource(Plants, '/plants')
api.add_resource(PlantByID, '/plants/<int:plant_id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

