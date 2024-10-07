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
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# Todo: Place your REST API code here ...
@app.route("/orders", methods=["POST"])
def create_order():
    """Create an Order"""
    app.logger.info("Request to create an Order")

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
    # UPDATE AN ORDER
######################################################################

@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """Updates an order"""
    app.logger.info(f"Request to update order id:{order_id}")

    #Check if order exists
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
        )

    # Update order with info in the json request
    app.logger.debug("Payload = %s", api.payload)

    data = api.payload
    order.deserialize(data)
    
    order.id = order_id
    order.update()
    return order.serialize(), status.HTTP_200_OK




