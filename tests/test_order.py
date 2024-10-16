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
# cspell:ignore userid
"""
Test cases for Order Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Order, Item, DataValidationError, db
from tests.factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        O R D E R   M O D E L   T E S T   C A S E S
######################################################################
class TestOrder(TestCase):
    """Order Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_order(self):
        """It should Create an Order and assert that it exists"""
        fake_order = OrderFactory()
        # pylint: disable=unexpected-keyword-arg
        order = Order(
            id=fake_order.id,
            customer_name=fake_order.customer_name,
            status=fake_order.status,
            created_at=fake_order.created_at.isoformat(),
            updated_at=fake_order.updated_at.isoformat(),
            items=fake_order.items,
        )

        self.assertIsNotNone(order)
        self.assertEqual(order.id, fake_order.id)
        self.assertEqual(order.customer_name, fake_order.customer_name)
        self.assertEqual(order.status, fake_order.status)
        self.assertEqual(order.created_at, fake_order.created_at.strftime("%Y-%m-%d"))
        self.assertEqual(order.updated_at, fake_order.updated_at.strftime("%Y-%m-%d"))
        self.assertEqual(len(order.items), len(fake_order.items))

    def test_add_a_order(self):
        """It should Create an order and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

    @patch("service.models.db.session.commit")
    def test_add_order_failed(self, exception_mock):
        """It should not create an Order on database error"""
        exception_mock.side_effect = Exception()
        order = OrderFactory()
        self.assertRaises(DataValidationError, order.create)

    def test_read_order(self):
        """It should Read an order"""
        order = OrderFactory()
        order.create()

        # Read it back
        found_order = Order.find(order.id)
        self.assertIsNotNone(found_order)
        self.assertEqual(found_order.id, order.id)
        self.assertEqual(found_order.customer_name, order.customer_name)
        self.assertEqual(found_order.status, order.status)
        self.assertEqual(found_order.created_at, order.created_at)
        self.assertEqual(found_order.updated_at, order.updated_at)
        self.assertEqual(len(found_order.items), 0)

    def test_list_all_orders(self):
        """It should List all Orders in the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        for order in OrderFactory.create_batch(5):
            order.create()
        # Assert that there are 5 orders in the database
        orders = Order.all()
        self.assertEqual(len(orders), 5)

    def test_find_by_name(self):
        """It should Find an Order by name"""
        order = OrderFactory()
        order.create()

        # Fetch it back by name
        same_order = Order.find_by_name(order.customer_name)[0]
        self.assertEqual(same_order.id, order.id)
        self.assertEqual(same_order.customer_name, order.customer_name)

    def test_serialize_an_order(self):
        """It should Serialize an order"""
        order = OrderFactory()
        item = ItemFactory()
        order.items.append(item)
        serial_order = order.serialize()
        self.assertEqual(serial_order["id"], order.id)
        self.assertEqual(serial_order["customer_name"], order.customer_name)
        self.assertEqual(serial_order["status"], order.status)
        self.assertEqual(serial_order["created_at"], str(order.created_at))
        self.assertEqual(serial_order["updated_at"], str(order.updated_at))
        self.assertEqual(len(serial_order["items"]), 1)
        items = serial_order["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["order_id"], item.order_id)
        self.assertEqual(items[0]["product_name"], item.product_name)
        self.assertEqual(items[0]["quantity"], item.quantity)
        self.assertEqual(items[0]["price"], item.price)
        self.assertEqual(items[0]["created_at"], item.created_at.isoformat())
        self.assertEqual(items[0]["updated_at"], item.updated_at.isoformat())

    def test_deserialize_an_order(self):
        """It should Deserialize an order"""
        order = OrderFactory()
        order.items.append(ItemFactory())
        order.create()
        serial_order = order.serialize()
        new_order = Order()
        new_order.deserialize(serial_order)
        self.assertEqual(new_order.customer_name, order.customer_name)
        self.assertEqual(new_order.status, order.status)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an order with a KeyError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an order with a TypeError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an item with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an item with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])

    def test_create_order_with_no_customer_name(self):
        """It should not Create an Order without a customer name"""
        order = Order()
        self.assertRaises(DataValidationError, order.create)

    def test_update_order_not_found(self):
        """It should not Update an Order that's not found"""
        order = OrderFactory()
        order.id = 0  # Set to an ID that doesn't exist
        self.assertRaises(DataValidationError, order.update)

    def test_delete_order_not_found(self):
        """It should not Delete an Order that's not found"""
        order = OrderFactory()
        order.id = 0  # Set to an ID that doesn't exist
        self.assertRaises(DataValidationError, order.delete)
