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

from unittest.mock import patch

from service.models import DataValidationError, Item, Order, OrderStatus
from tests.factories import ItemFactory, OrderFactory
from tests.test_base import TestBase


######################################################################
#        O R D E R   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrder(TestBase):
    """Order Model Test Cases"""

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

    def test_create_an_order_with_default_status(self):
        """It should Create an Order without status
        which is set and assert that the status is set to the default value"""
        fake_order = OrderFactory()
        # pylint: disable=unexpected-keyword-arg
        order = Order(
            # no status set so expecting a default of CREATED
            id=fake_order.id,
            customer_name=fake_order.customer_name,
        )
        order.create()

        self.assertIsNotNone(order)
        self.assertEqual(order.status, OrderStatus.CREATED)

    def test_serialize_invalid_status(self):
        """It should raise a DataValidationError when serializing an invalid status"""
        order = OrderFactory()
        order.status = "INVALID_STATUS"  # Directly set an invalid status
        with self.assertRaises(DataValidationError):
            order.serialize()

    def test_deserialize_invalid_status(self):
        """It should raise a DataValidationError when deserializing an invalid status"""
        order = Order()
        invalid_data = {
            "customer_name": "John Doe",
            "status": "INVALID_STATUS",
            "items": [],
        }
        with self.assertRaises(DataValidationError) as context:
            order.deserialize(invalid_data)
        self.assertIn(
            "Invalid status value 'INVALID_STATUS' not in OrderStatus Enum",
            str(context.exception),
        )

    def test_deserialize_no_status_feild(self):
        """It should assign status a CREATED enum as a default"""
        order = OrderFactory()
        order.items.append(ItemFactory())
        order.create()
        serial_order = order.serialize()
        if "status" in serial_order:
            del serial_order["status"]
        new_order = Order()
        new_order.deserialize(serial_order)
        self.assertEqual(new_order.customer_name, order.customer_name)
        self.assertEqual(new_order.status, OrderStatus.CREATED)

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
        same_order = Order.find_by_filters(customer_name=order.customer_name)[0]
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
        self.assertEqual(serial_order["status"], order.status.value)
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

    def test_find_by_order_status(self):
        """It should Find Orders by order status"""
        orders = OrderFactory.create_batch(10)
        for order in orders:
            order.create()
        order_status = orders[0].status
        count = len([order for order in orders if order.status == order_status])
        found = Order.find_by_filters(order_status=order_status.value)
        self.assertEqual(len(found), count)
        for order in found:
            self.assertEqual(order.status, order_status)

    def test_find_by__invalid_order_status(self):
        """It should Find empty list for invalid order status queried"""
        orders = OrderFactory.create_batch(10)
        for order in orders:
            order.create()
        order_status = "INVALID_STATUS"
        count = len([order for order in orders if order.status.value == order_status])
        found = Order.find_by_filters(order_status=order_status)
        self.assertEqual(len(found), count)
        self.assertEqual(len(found), 0)
        self.assertEqual(count, 0)

    def test_find_by_product_name(self):
        """It should Find an Order by product_name"""
        order = OrderFactory()
        item = ItemFactory()
        order.items.append(item)
        order.create()

        same_order = Order.find_by_filters(product_name=item.product_name)[0]
        self.assertEqual(same_order.id, order.id)
        self.assertEqual(same_order.items[0].product_name, item.product_name)

    def test_find_by_invalid_product_name(self):
        """It should Find empty list for non-existing product_name queried"""
        order = OrderFactory()
        item = ItemFactory()
        order.items.append(item)
        order.create()

        orders = Order.find_by_filters(product_name="IMPOSSIBLE PRODUCT")
        self.assertEqual(len(orders), 0)
