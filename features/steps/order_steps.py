import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("the following orders")
def step_impl(context):
    """Delete all Orders and load new ones"""
    # List all orders and delete them one by one
    rest_endpoint = f"{context.base_url}/api/orders"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK
    for order in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{order['id']}")
        assert context.resp.status_code == HTTP_204_NO_CONTENT

    # Load the database with new orders
    for row in context.table:
        payload = {
            "customer_name": row["customer_name"],
            "status": row["status"],
            "items": [
                {
                    "product_name": row["product_name"],
                    "quantity": int(row["quantity"]),
                    "price": float(row["price"]),
                }
            ],
        }

        # Debug print to see what we're sending
        print(f"Sending payload: {payload}")

        context.resp = requests.post(rest_endpoint, json=payload)
        assert context.resp.status_code == HTTP_201_CREATED
