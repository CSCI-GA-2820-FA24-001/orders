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
Test cases for Item Model
"""

from service.models import DataValidationError, Item, Order
from tests.factories import ItemFactory, OrderFactory
# Local application imports
from tests.test_base import TestBase

######################################################################
#        I T E M   M O D E L   T E S T   C A S E S
######################################################################


######################################################################
#  T E S T   C A S E S
######################################################################


class TestItem(TestBase):
    """Test suite for the Item model.

    This class contains unit tests that verify the functionality
    of the Item model, including creation, serialization,
    deserialization, and other core operations.
    """

    def test_add_order_item(self):
        """It should Create an order with an item and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        self.assertEqual(new_order.items[0].product_name, item.product_name)

        item2 = ItemFactory(order=order)
        order.items.append(item2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 2)
        self.assertEqual(new_order.items[1].product_name, item2.product_name)

    def test_serialize_an_item(self):
        """It should serialize an Item"""
        item = ItemFactory()
        serial_item = item.serialize()
        self.assertEqual(serial_item["id"], item.id)
        self.assertEqual(serial_item["order_id"], item.order_id)
        self.assertEqual(serial_item["product_name"], item.product_name)
        self.assertEqual(serial_item["quantity"], item.quantity)
        self.assertEqual(serial_item["price"], item.price)
        self.assertEqual(serial_item["created_at"], item.created_at.isoformat())
        self.assertEqual(serial_item["updated_at"], item.updated_at.isoformat())

    def test_deserialize_an_item(self):
        """It should deserialize an Item"""
        item = ItemFactory()
        item.create()
        new_item = Item()
        new_item.deserialize(item.serialize())
        self.assertEqual(new_item.product_name, item.product_name)
        self.assertEqual(new_item.quantity, item.quantity)
        self.assertEqual(new_item.price, item.price)

    def test_item_repr(self):
        """It should return a string representation of the item"""
        item = ItemFactory()
        self.assertIn(str(item.id), repr(item))
        self.assertIn(item.product_name, repr(item))

    def test_update_item_not_found(self):
        """It should not Update an Item that's not found"""
        item = ItemFactory()
        item.id = 0  # Set to an ID that doesn't exist
        self.assertRaises(DataValidationError, item.update)

    def test_delete_item_not_found(self):
        """It should not Delete an Item that's not found"""
        item = ItemFactory()
        item.id = 0  # Set to an ID that doesn't exist
        self.assertRaises(DataValidationError, item.delete)
