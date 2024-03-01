from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class Restaurants(Resource):
    def get(self):
        restaurants = [{"id": restaurant.id, "name": restaurant.name, "address": restaurant.address}
                       for restaurant in Restaurant.query.all()]
        return make_response(jsonify(restaurants), 200)

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

        restaurant_data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "pizzas": []
        }

        for pizza in restaurant.pizzas:
            pizza_data = {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            }
            restaurant_data["pizzas"].append(pizza_data)

        return make_response(jsonify(restaurant_data), 200)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

        RestaurantPizza.query.filter_by(restaurant_id=id).delete()

        db.session.delete(restaurant)
        db.session.commit()
        return make_response(jsonify({}), 200)

class Pizzas(Resource):
    def get(self):
        pizzas = [{"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients}
                  for pizza in Pizza.query.all()]
        return make_response(jsonify(pizzas), 200)

class RestaurantPizza(Resource):
    def post(self):
        data = request.json
        price, pizza_id, restaurant_id = data.get('price'), data.get('pizza_id'), data.get('restaurant_id')

        if not all([price, pizza_id, restaurant_id]):
            return jsonify({"errors": ["Missing required fields"]}), 400

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404

        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)

        db.session.add(restaurant_pizza)
        db.session.commit()

        pizza_data = {
            "id": restaurant_pizza.pizza.id,
            "name": restaurant_pizza.pizza.name,
            "ingredients": restaurant_pizza.pizza.ingredients
        }

        return make_response(jsonify(pizza_data), 201)

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizza, "/restaurant_pizzas")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
