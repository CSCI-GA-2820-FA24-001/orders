######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Order Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Order
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.common import status  # HTTP Status Codes
from service.models import Order, Item


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Order REST API Service",
            version="1.0",
            paths=url_for("list_orders", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@app.route("/orders", methods=["POST"])
def create_order():
    """Create an Order"""
    app.logger.info("Request to create an Order")
    check_content_type("application/json")

    # Create the order
    order = Order()
    order.deserialize(request.get_json())
    order.create()

    # Create a message to return
    message = order.serialize()
    location_url = url_for("read_order", order_id=order.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


@app.route("/orders/<int:order_id>", methods=["GET"])
def read_order(order_id):
    """Retrieve a single order"""
    app.logger.info("Request for Order with id: %s", order_id)

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# LIST ALL ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request for Order list")
    orders = []

    # Process the query string if any
    name = request.args.get("name")
    if name:
        orders = Order.find_by_name(name)
    else:
        orders = Order.all()

    # Return as an array of dictionaries
    results = [order.serialize() for order in orders]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# LIST ITEMS IN AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_items_in_order(order_id):
    """Returns all of the Items for an Order"""
    app.logger.info("Request for all Items for Order with id: %s", order_id)

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Get the items for the order
    results = [item.serialize() for item in order.items]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# UPDATE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """Updates an order"""
    app.logger.info(f"Request to update order id:{order_id}")
    print("Called1")
    # Check if order exists
    print("Called2")
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")
    print("Called3")
    # Update order with info in the json request
    data = request.get_json()
    app.logger.debug("Payload received for update: %s", data)

    data = request.get_json()
    order.deserialize(data)
    order.id = order_id
    order.update()
    # Return the updated order
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN ITEM IN AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_item_order(order_id, item_id):
    """Updates an order"""
    app.logger.info(
        f"Request to update item {item_id} in order with order id:{order_id}"
    )
    # Check if order exists
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Check if item exists
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{item_id}' could not be found.",
        )

    # Update item with info in the json request
    data = request.get_json()
    app.logger.debug("Payload received for update: %s", data)
    item.deserialize(data)
    item.id = item_id
    if item:
        Item.update(item)
    # Return the updated order
    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# ADD AN ITEM TO AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["POST"])
def create_items(order_id):
    """
    Create an Item on an Order

    This endpoint will add an item to an order
    """
    app.logger.info("Request to create an Item for Order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the item to the order
    order.items.append(item)
    order.update()

    # Prepare a message to return
    message = item.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_items", order_id=order.id, item_id=item.id, _external=True
    )

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# RETRIEVE AN ITEM FROM ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_items(order_id, item_id):
    """
    Get an Item

    This endpoint returns just an item
    """
    app.logger.info("Request to retrieve Item %s for Order id: %s", (item_id, order_id))

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{item_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )


######################################################################
# DELETE AN ORDER WITH ORDER ID
######################################################################


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """Delete an entire order"""
    app.logger.info("Request to delete an entire order with order id: %s", order_id)

    # See if the order first exists
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with order id '{order_id}' is not found and hence cannot be deleted",
        )
    order.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# DELETE AN ITEM FROM AN ORDER
######################################################################


@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item_from_order(order_id, item_id):
    """Delete an item from an order"""
    app.logger.info("Request to delete Item %s from Order id: %s", (item_id, order_id))
    # Check if order exists
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )
    item.delete()
    return "", status.HTTP_204_NO_CONTENT


@app.route("/trigger_500", methods=["GET"])
def trigger_500():
    abort(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Test internal server error",
    )
