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
Order Service with Swagger

This service implements a REST API that allows you to Create, Read, Update
and Delete Order
"""

from flask import request
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse, Api
from service.models import Order, Item, OrderStatus
from service.common import status  # HTTP Status Codes

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Order Demo REST API Swagger Service",
    description="This is a Order server.",
    default="orders",
    default_label="Order service operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    prefix="/api",
)


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
base_item_model = api.model(
    "Item",
    {
        "product_name": fields.String(
            required=True, description="The name of the product"
        ),
        "quantity": fields.Integer(required=True, description="Quantity of item"),
        # pylint: disable=protected-access
        "price": fields.Float(required=True, description="Price of quantity of item"),
    },
)

item_model = api.inherit(
    "ItemModel",
    base_item_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "order_id": fields.Integer(
            readOnly=True,
            description="The unique order id assigned internally by service",
        ),
    },
)

# Define the model so that the docs reflect what can be sent
base_order_model = api.model(
    "Order",
    {
        "customer_name": fields.String(
            required=True, description="The name of the customer"
        ),
        "status": fields.String(
            enum=OrderStatus._member_names_, description="Status of the order"
        ),
        # pylint: disable=protected-access
        "items": fields.List(
            fields.Nested(item_model), description="The list of items in the Order"
        ),
    },
)

order_model = api.inherit(
    "OrderModel",
    base_order_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments: customer_name, order_status and product_name
order_args = reqparse.RequestParser()
order_args.add_argument(
    "name",
    type=str,
    location="args",
    required=False,
    help="List orders by customer name",
)
order_args.add_argument(
    "order_status",
    type=str,
    location="args",
    required=False,
    help="List orders by status",
)
order_args.add_argument(
    "product_name",
    type=str,
    location="args",
    required=False,
    help="List orders by product_name in items",
)


######################################################################
#  PATH: /orders/<int:order_id>
######################################################################
@api.route("/orders/<int:order_id>")
@api.param("order_id", "The order identifier")
class OrderResource(Resource):
    """
    OrderResource class

    Allows the manipulation of a single Order
    GET /order{id} - Returns an Order with the id
    PUT /order{id} - Update an Order with the id
    DELETE /order{id} -  Deletes an Order with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ORDER
    # ------------------------------------------------------------------
    @api.doc("get_order")
    @api.response(404, "Order not found")
    @api.marshal_with(order_model)
    def get(self, order_id):
        """Retrieve a single order"""
        app.logger.info("Request for Order with id: %s", order_id)

        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )

        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ORDER
    # ------------------------------------------------------------------
    @api.doc("update_order")
    @api.response(404, "Order not found")
    @api.response(400, "The posted Order data was not valid")
    @api.expect(order_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Updates an order"""
        app.logger.info(f"Request to update order id:{order_id}")
        # Check if order exists
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )
        # Update order with info in the json request
        data = api.payload
        app.logger.debug("Payload received for update: %s", data)
        order.deserialize(data)
        order.id = order_id
        order.update()
        # Return the updated order
        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ORDER
    # ------------------------------------------------------------------
    @api.doc("delete_order")
    @api.response(204, "Order deleted")
    def delete(self, order_id):
        """Delete an entire order"""
        app.logger.info("Request to delete an entire order with order id: %s", order_id)

        # See if the order first exists
        order = Order.find(order_id)
        if order:
            order.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders
######################################################################
@api.route("/orders", strict_slashes=False)
class OrderCollection(Resource):
    """Handles all interactions with collections of Pets"""

    # ------------------------------------------------------------------
    # LIST ALL ORDERS
    # ------------------------------------------------------------------
    @api.doc("list_orders")
    @api.expect(order_args, validate=True)
    @api.marshal_list_with(order_model)
    def get(self):
        """Returns all of the Orders"""
        app.logger.info("Request to list Orders...")
        orders = []
        args = order_args.parse_args()
        customer_name = args["name"]
        order_status = args["order_status"]
        product_name = args["product_name"]

        orders = Order.find_by_filters(
            customer_name=customer_name,
            order_status=order_status,
            product_name=product_name,
        )

        # Return as an array of dictionaries
        results = [order.serialize() for order in orders]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW ORDER
    # ------------------------------------------------------------------
    @api.doc("create_order")
    @api.response(400, "The posted data was not valid")
    @api.expect(base_order_model)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """Create an Order"""
        app.logger.info("Request to create an Order")

        # Create the order
        order = Order()
        order.deserialize(api.payload)
        order.create()

        # Create a message to return
        message = order.serialize()
        location_url = api.url_for(OrderResource, order_id=order.id, _external=True)

        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /orders/<int:order_id>/cancel
######################################################################
@api.route("/orders/<int:order_id>/cancel")
@api.param("order_id", "The order identifier")
class CancelOrderResource(Resource):
    """Cancel actions on a Order"""

    @api.doc("cancel_order")
    @api.response(404, "Order not found")
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Cancels an order"""
        app.logger.info(f"Request to cancel order id:{order_id}")
        # Check if order exists
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        app.logger.info(
            f"Changing status of order with order id:{order_id} to CANCELLED"
        )
        order.status = OrderStatus.CANCELLED
        order.update()
        app.logger.info(f"{order}")
        # Return the updated order
        return order.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /orders/<int:order_id>/status
######################################################################
@api.route("/orders/<int:order_id>/status")
@api.param("order_id", "The order identifier")
class UpdateStatusResource(Resource):
    """Update status actions on a Order"""

    @api.doc("update_order_status")
    @api.response(404, "Order not found")
    @api.response(400, "The posted Order data was not valid")
    @api.expect(order_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Update the status of an Order"""
        app.logger.info(
            "Request to update order status for order with id: %s", order_id
        )

        # Find the order by ID
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        # Get the new status from request body
        data = api.payload
        if not data or "status" not in data:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Required field 'status' missing from request body",
            )

        try:
            new_status = OrderStatus(data["status"].upper())

            # If current status is Cancelled, don't allow any changes
            if order.status == OrderStatus.CANCELLED:
                abort(
                    status.HTTP_400_BAD_REQUEST,
                    "Cannot update status of a cancelled order",
                )

            # If the status is not changing, return success (idempotent)
            if order.status == new_status:
                return order.serialize(), status.HTTP_200_OK

            # Update the status
            order.status = new_status
            order.update()
            return order.serialize(), status.HTTP_200_OK

        except ValueError as error:
            abort(status.HTTP_400_BAD_REQUEST, f"Invalid status value: {str(error)}")


######################################################################
#  PATH: /orders/<int:order_id>/items
######################################################################
@api.route("/orders/<int:order_id>/items")
@api.param("order_id", "The order identifier")
class ItemCollection(Resource):
    """
    ItemCollection class

    Allows the manipulation of a items in an Order
    GET /order{id}/items - Returns an items in an order with order_id
    POST /order{id}/items - Add an item to an Order with the id
    """

    # ------------------------------------------------------------------
    # LIST ALL ITEMS IN AN ORDER
    # ------------------------------------------------------------------
    @api.doc("get_items_in_order")
    @api.response(404, "Order not found")
    @api.marshal_with(item_model)
    def get(self, order_id):
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

        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD AN ITEM IN AN ORDER
    # ------------------------------------------------------------------
    @api.doc("add_item_in_order")
    @api.response(404, "Order not found")
    @api.response(400, "The posted item data was not valid")
    @api.expect(base_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """
        Create an Item on an Order

        This endpoint will add an item to an order
        """
        app.logger.info("Request to create an Item for Order with id: %s", order_id)
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
        location_url = api.url_for(
            ItemResource, order_id=order.id, item_id=item.id, _external=True
        )

        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /orders/<int:order_id>/items/<int:item_id>
######################################################################
@api.route("/orders/<int:order_id>/items/<int:item_id>")
@api.param("order_id", "The order identifier")
@api.param("item_id", "The item identifier")
class ItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Order
    GET /order{id}/item{id} - Returns an item in an Order
    PUT /order{id}/item{id} - Update an item with id in order with the id
    DELETE /order{id}/item{id} -  Deletes an item with id in order with id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ITEM IN ORDER
    # ------------------------------------------------------------------
    @api.doc("get_item")
    @api.response(404, "Order not found")
    @api.marshal_with(item_model)
    def get(self, order_id, item_id):
        """
        Get an Item

        This endpoint returns just an item
        """
        app.logger.info(
            "Request to retrieve Item %s for Order id: %s", item_id, order_id
        )

        # See if the item exists and abort if it doesn't
        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{item_id}' could not be found.",
            )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN ITEM IN AN EXISTING ORDER
    # ------------------------------------------------------------------
    @api.doc("update_item_in_order")
    @api.response(404, "Order not found")
    @api.response(404, "Item not found")
    @api.response(400, "The posted item data was not valid")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, order_id, item_id):
        """Updates an item in an order"""
        app.logger.info(
            f"Request to update item {item_id} in order with order id:{order_id}"
        )
        # Check if order exists
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        # Check if item exists
        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{item_id}' could not be found.",
            )

        # Update item with info in the json request
        data = api.payload
        app.logger.debug("Payload received for update: %s", data)
        item.deserialize(data)
        item.id = item_id
        if item:
            Item.update(item)
        # Return the updated order
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ITEM FROM ORDER
    # ------------------------------------------------------------------
    @api.doc("delete_item_from_order")
    @api.response(204, "Order deleted")
    @api.response(404, "Order not found")
    def delete(self, order_id, item_id):
        """Delete an item from an order"""
        app.logger.info(f"Request to delete Item {item_id} from Order id: {order_id}")
        # Check if order exists
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )
        item = Item.find(item_id)
        if item:
            item.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /trigger_500
######################################################################
@api.route("/trigger_500", strict_slashes=False)
class TriggerResource(Resource):
    """Tests internal server error"""

    @api.doc("internal_server_tests")
    def get(self):
        """Tests internal server error"""
        abort(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Test internal server error",
        )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
