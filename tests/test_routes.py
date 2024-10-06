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
TestOrder API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order
from tests.factories import OrderFactory, ItemFactory
from factory import Faker

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrderService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_orders(self, count):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            order = OrderFactory()
            ## To-do: remove debug log once all testing is done
            print(order)
            resp = self.client.post(BASE_URL, json=order.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
        return orders

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        """It should Create a new Order"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = resp.get_json()
        self.assertEqual(new_order["status"], order.status, "status does not match")
        self.assertEqual(
            new_order["customer_name"],
            order.customer_name,
            "customer_name does not match",
        )
        self.assertEqual(new_order["items"], order.items, "items does not match")

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()
        self.assertEqual(new_order["status"], order.status, "status does not match")
        self.assertEqual(
            new_order["customer_name"],
            order.customer_name,
            "customer_name does not match",
        )
        self.assertEqual(new_order["items"], order.items, "items does not match")

    def test_read_order(self):
        """It should Read a single Order"""
        # get the id of an order
        order = self._create_orders(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{order.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_name"], order.customer_name)

    def test_read_order_not_found(self):
        """It should not Read an Order that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_list(self):
        """It should Get a list of Orders"""
        self._create_orders(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_order_list_empty(self):
        """It should Get an empty list of Orders when no order is present"""
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_get_order_by_name(self):
        """It should Get an Order by customer name"""
        orders = self._create_orders(3)
        resp = self.client.get(BASE_URL, query_string=f"customer_name={orders[0].customer_name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["customer_name"], orders[0].customer_name)

    def test_get_order_by_name_empty(self):
        """It should not Get an empty list of Orders for customer_name that does not exist in db"""
        customer_name = Faker("name")
        resp = self.client.get(BASE_URL, query_string=f"customer_name={customer_name}")
        print(resp)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    ######################################################################
    #  I T E M S  I N  A N  O R D E R   T E S T   C A S E S
    ######################################################################

    ## Uncomment below when CREATE_ITEM_IN_ORDER is implemented
    # def test_get_items_in_list(self):
    #     """It should Get a list of Items in an order with order_id"""
    #     # add two items to order
    #     order = self._create_orders(1)[0]
    #     item_list = ItemFactory.create_batch(2)

    #     # Create item 1
    #     resp = self.client.post(
    #         f"{BASE_URL}/{order.id}/items", json=item_list[0].serialize()
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    #     # Create item 2
    #     resp = self.client.post(
    #         f"{BASE_URL}/{order.id}/items", json=item_list[1].serialize()
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    #     # get the list back and make sure there are 2
    #     resp = self.client.get(f"{BASE_URL}/{order.id}/items")
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)

    #     data = resp.get_json()
    #     self.assertEqual(len(data), 2)
    #     self.assertEqual(data[0]["id"], item_list[0]["id"])
    #     self.assertEqual(data[1]["id"], item_list[1]["id"])