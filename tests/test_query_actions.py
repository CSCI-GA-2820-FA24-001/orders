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

import logging

from service.common import status
from service.models import OrderStatus
from tests.factories import ItemFactory, OrderFactory
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

    def test_update_order_status(self):
        """It should update an order's status"""
        # Create a new order
        order = self._create_orders(1)[0]

        # Test status update flow: Created -> In_Progress -> Shipped -> Completed
        status_flow = ["In_Progress", "Shipped", "Completed"]

        for new_status in status_flow:
            if order.status != OrderStatus.CANCELLED:
                resp = self.client.put(
                    f"{BASE_URL}/{order.id}/status",
                    json={"status": new_status},
                    content_type="application/json",
                )
                self.assertEqual(resp.status_code, status.HTTP_200_OK)
                data = resp.get_json()
                self.assertEqual(data["status"], new_status.upper())

    def test_update_order_idempotent(self):
        """It should be idempotent when updating to same status"""
        order = None
        while True:
            order = self._create_orders(1)[0]  # Create or fetch an order
            if order.status != OrderStatus.CANCELLED:
                break  # Exit the loop if the status is NOT CANCELLED

        curr_status = order.status

        # Try to update with the same status
        if curr_status != OrderStatus.CANCELLED:
            resp = self.client.put(
                f"{BASE_URL}/{order.id}/status",
                json={"status": curr_status.value},
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            data = resp.get_json()
            self.assertEqual(data["status"], curr_status.value)

    def test_update_cancelled_order_status(self):
        """It should not update status of cancelled order"""
        order = self._create_orders(1)[0]

        # First cancel the order
        if order.status != OrderStatus.CANCELLED:
            resp = self.client.put(
                f"{BASE_URL}/{order.id}/status",
                json={"status": "Cancelled"},
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Try to update cancelled order's status
        resp = self.client.put(
            f"{BASE_URL}/{order.id}/status",
            json={"status": "In_Progress"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_invalid(self):
        """It should not update status with invalid value"""
        order = self._create_orders(1)[0]
        invalid_status = "INVALID_STATUS"

        resp = self.client.put(
            f"{BASE_URL}/{order.id}/status",
            json={"status": invalid_status},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_not_found(self):
        """It should not update status of non-existent order"""
        resp = self.client.put(
            f"{BASE_URL}/0/status",
            json={"status": "In_Progress"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_status_bad_request(self):
        """It should not update status with missing status field"""
        order = self._create_orders(1)[0]
        resp = self.client.put(
            f"{BASE_URL}/{order.id}/status", json={}, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_order_by_product_name(self):
        """It should Get Orders by product name"""
        order = self._create_orders(3)[0]
        item = ItemFactory.create()
        resp = self.client.post(f"{BASE_URL}/{order.id}/items", json=item.serialize())
        resp = self.client.get(
            BASE_URL, query_string=f"product_name={item.product_name}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], order.id)

    def test_get_order_by_product_name_empty(self):
        """It should Get an empty list of Orders for product_name that does not exist in db"""
        order = self._create_orders(3)[0]
        item = ItemFactory.create()
        item.product_name = "productA"
        resp = self.client.post(f"{BASE_URL}/{order.id}/items", json=item.serialize())

        resp = self.client.get(BASE_URL, query_string="product_name=productB")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_cancel_order(self):
        """It should cancel an existing Order"""
        # Create an order to update
        order = self._create_orders(1)[0]

        # POST request to create the order
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_order = resp.get_json()
        new_order_id = new_order["id"]

        # Send a PUT request to update the order
        resp = self.client.put(
            f"{BASE_URL}/{new_order_id}/cancel",
            json=new_order,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        updated_order = resp.get_json()
        self.assertEqual(updated_order["status"], "CANCELLED")

    def test_cancel_order_not_found(self):
        """It should not cancel an order that is not found"""
        test_order = OrderFactory()
        invalid_order_id = test_order.id - 1
        resp = self.client.put(
            f"{BASE_URL}/{invalid_order_id}/cancel", json=test_order.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------
    def test_query_by_order_status(self):
        """It should Query Orders by order status"""
        orders = self._create_orders(5)
        completed_orders = [
            order for order in orders if order.status == OrderStatus.COMPLETED
        ]
        completed_count = len(completed_orders)
        logging.debug("Completed Orders [%d] %s", completed_count, completed_orders)

        # test for available
        response = self.client.get(BASE_URL, query_string="order_status=completed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), completed_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], OrderStatus.COMPLETED.value)

    def test_create_order_bad_order_status(self):
        """It should not Create an Order with bad order status data"""
        order = OrderFactory()
        logging.debug(order)
        # change status to a bad string
        test_order = order.serialize()
        test_order["status"] = "INVALID_STATUS"  # invalid status
        response = self.client.post(BASE_URL, json=test_order)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
