"""
Order Steps
Steps file for orders.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
from behave import given
from compare import expect


@given('the following orders')
def step_impl(context):
    """ Delete all Orders and load new ones """
    # List of orders from the context
    for row in context.table:
        data = {
            "customer_name": row['customer_name'],
            "status": row['status'],
            "items": [{
                "product_name": row['product_name'],
                "quantity": int(row['quantity']),
                "price": float(row['price'])
            }]
        }

        context.resp = context.app.post('/orders', json=data)
        expect(context.resp.status_code).to_equal(201)