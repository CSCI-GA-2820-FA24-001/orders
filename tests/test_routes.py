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

from factory import Faker

from service.common import status
from tests.factories import OrderFactory
from tests.test_base import TestBase

BASE_URL = "/api/orders"


######################################################################
#  T E S T   C A S E S
######################################################################


class TestOrderService(TestBase):
    """REST API Server Tests"""

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

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
        self.assertEqual(
            new_order["status"], order.status.value, "status does not match"
        )
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
        self.assertEqual(
            new_order["status"], order.status.value, "status does not match"
        )
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

    def test_update_order(self):
        """It should update an existing Order"""
        # Create an order to update
        order = self._create_orders(1)[0]

        # POST request to create the order
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_order = resp.get_json()
        new_order["customer_name"] = "John Doe"
        new_order_id = new_order["id"]

        # Send a PUT request to update the order
        resp = self.client.put(
            f"{BASE_URL}/{new_order_id}",
            json=new_order,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        updated_order = resp.get_json()
        self.assertEqual(updated_order["customer_name"], "John Doe")

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
        resp = self.client.get(
            BASE_URL, query_string=f"customer_name={orders[0].customer_name}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["customer_name"], orders[0].customer_name)

    def test_get_order_by_name_empty(self):
        """It should not Get an empty list of Orders for customer_name that does not exist in db"""
        customer_name = Faker("name")
        resp = self.client.get(BASE_URL, query_string=f"customer_name={customer_name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_delete_order(self):
        """It should Delete an entire order by order id"""
        order = self._create_orders(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        response = self.client.get(
            f"{BASE_URL}/{order.id}", content_type="application/json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )  # 404 error after the fact

    def test_delete_order_by_orderid_empty(self):
        """It should return an error code when you try to delete an order which does not exist"""
        resp = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_order_list_by_name(self):
        """It should Get a list of Orders by name"""
        orders = self._create_orders(3)
        test_name = orders[0].customer_name
        name_orders = [order for order in orders if order.customer_name == test_name]
        resp = self.client.get(BASE_URL, query_string=f"name={test_name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(name_orders))
        for order in data:
            self.assertEqual(order["customer_name"], test_name)

    def test_update_order_not_found(self):
        """It should not Update an order that is not found"""
        test_order = OrderFactory()
        resp = self.client.put(f"{BASE_URL}/0", json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_bad_request(self):
        """It should not Update an order with bad data"""
        test_order = self._create_orders(1)[0]
        resp = self.client.put(
            f"{BASE_URL}/{test_order.id}", json={"bad_key": "bad_value"}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
