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
from datetime import datetime
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order
from tests.factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################


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

    def test_health(self):
        """It should get the health endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_add_item(self):
        """It should add an item to an order"""
        order = self._create_orders(1)[0]
        now = datetime.utcnow()
        item = ItemFactory(
            order_id=order.id,
            created_at=now,
            updated_at=now,
        )
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], item.order_id)
        self.assertEqual(data["product_name"], item.product_name)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(float(data["price"]), float(item.price))

        # Parse the datetime strings
        returned_created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%dT%H:%M:%S.%f"
        )
        returned_updated_at = datetime.strptime(
            data["updated_at"], "%Y-%m-%dT%H:%M:%S.%f"
        )

        # Zero out microseconds
        returned_created_at = returned_created_at.replace(microsecond=0)
        returned_updated_at = returned_updated_at.replace(microsecond=0)
        item_created_at = item.created_at.replace(microsecond=0)
        item_updated_at = item.updated_at.replace(microsecond=0)

        # Compare the timestamps
        self.assertEqual(returned_created_at, item_created_at)
        self.assertEqual(returned_updated_at, item_updated_at)

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        self.assertEqual(new_item["order_id"], item.order_id)
        self.assertEqual(new_item["product_name"], item.product_name)
        self.assertEqual(new_item["quantity"], item.quantity)
        self.assertEqual(float(new_item["price"]), float(item.price))

        # Parse and zero out microseconds
        returned_created_at = datetime.strptime(
            new_item["created_at"], "%Y-%m-%dT%H:%M:%S.%f"
        ).replace(microsecond=0)
        returned_updated_at = datetime.strptime(
            new_item["updated_at"], "%Y-%m-%dT%H:%M:%S.%f"
        ).replace(microsecond=0)

        # Compare the timestamps
        self.assertEqual(returned_created_at, item_created_at)
        self.assertEqual(returned_updated_at, item_updated_at)

    def test_get_item(self):
        """It should Get an item from an order"""
        # create a known item
        order = self._create_orders(1)[0]
        now = datetime.utcnow()
        item = ItemFactory(
            order_id=order.id,
            created_at=now,
            updated_at=now,
        )
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_name"], item.product_name)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(float(data["price"]), float(item.price))

        # Parse the datetime strings
        returned_created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%dT%H:%M:%S.%f"
        )
        returned_updated_at = datetime.strptime(
            data["updated_at"], "%Y-%m-%dT%H:%M:%S.%f"
        )

        # Zero out microseconds
        returned_created_at = returned_created_at.replace(microsecond=0)
        returned_updated_at = returned_updated_at.replace(microsecond=0)
        item_created_at = item.created_at.replace(microsecond=0)
        item_updated_at = item.updated_at.replace(microsecond=0)

        # Compare the timestamps
        self.assertEqual(returned_created_at, item_created_at)
        self.assertEqual(returned_updated_at, item_updated_at)

    def test_get_items_in_list(self):
        """It should Get a list of Items in an order with order_id"""
        # add two items to order
        order = self._create_orders(1)[0]
        item_list = ItemFactory.create_batch(2)

        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{order.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["product_name"], item_list[0].product_name)
        self.assertEqual(data[1]["product_name"], item_list[1].product_name)

    def test_update_item(self):
        """It should update an item in an existing Order"""
        # Create an order to update
        order = self._create_orders(1)[0]

        # POST request to create the order
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        now = datetime.utcnow()
        item = ItemFactory(
            order_id=order.id,
            created_at=now,
            updated_at=now,
        )

        # POST request to create an item
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_item = resp.get_json()
        new_item["quantity"] = 10
        new_item_id = new_item["id"]

        # Send a PUT request to update the order
        resp = self.client.put(
            f"{BASE_URL}/{order.id}/items/{new_item_id}",
            json=new_item,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        updated_item = resp.get_json()
        self.assertEqual(updated_item["quantity"], 10)

    def test_delete_item_in_order(self):
        """It should delete an item in an order (item is present in the order)"""
        # Create an order to delete
        order = self._create_orders(1)[0]

        # POST request to create the order
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create an item
        item = ItemFactory()

        # POST request to create an item
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )

        # Verify that the item was created
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_item = resp.get_json()
        new_item_id = new_item["id"]

        # Now delete an item
        resp = self.client.delete(f"{BASE_URL}/{order.id}/items/{new_item_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{new_item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_in_order_which_does_not_exist(self):
        """It should not delete an item in an order which does not exist"""
        # Create an item to search in a non existent order
        item = ItemFactory()

        # POST request to create an item and pass it in an order which does not exist
        resp = self.client.post(
            f"{BASE_URL}/0/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        resp = self.client.delete(f"{BASE_URL}/0/items/{item.id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_not_in_order(self):
        """It should not delete an item which is not in an order"""
        # Create an order to delete
        order = self._create_orders(1)[0]

        # POST request to create the order
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.delete(f"{BASE_URL}/{order.id}/items/0")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_item_list_order_not_found(self):
        """It should return 404 when trying to get items for a non-existent order"""
        resp = self.client.get(f"{BASE_URL}/0/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_item_order_not_found(self):
        """It should return 404 when trying to add an item to a non-existent order"""
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/0/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_order_not_found(self):
        """It should return 404 when trying to update an item in a non-existent order"""
        item = ItemFactory()
        resp = self.client.put(
            f"{BASE_URL}/0/items/{item.id}",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_item_not_found(self):
        """It should return 404 when trying to update a non-existent item"""
        # Create an order to delete
        order = self._create_orders(1)[0]

        # POST request to create the order
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        item = ItemFactory()
        resp = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item.id}",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)