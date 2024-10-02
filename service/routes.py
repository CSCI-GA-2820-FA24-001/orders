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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.common import status  # HTTP Status Codes

from service.models import Order


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
@app.route("/orders/<int:orderid>", methods=["GET"])
def get_order(orderid):
    """Retrieve a single order"""
    app.logger.info("Request for Order with id: %s", orderid)

    # See if the account exists and abort if it doesn't
    order = Order.find(orderid)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{orderid}' could not be found.",
        )

    return jsonify(order.serialize()), status.HTTP_200_OK
