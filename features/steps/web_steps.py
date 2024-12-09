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

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions


@when('I visit the "Home Page"')
def step_impl(context):
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


position_mapping = {
    "First": 0,
    "Second": 1,
    "Third": 2,
    "Fourth": 3,
}


@then('I should see "{order_count}" orders')
def step_impl(context, order_count):
    container = context.driver.find_element(By.ID, "ordersContainer")
    orders = container.find_elements(By.XPATH, "./div")

    assert len(orders) == int(order_count), (
        f"Expected to see {order_count} orders, " f"but found {len(orders)}."
    )
    print(f"Success: Found {order_count} orders as expected.")


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(" ", "-") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@when('I press the "{button_class}" button for the "{position}" order')
def step_impl(context, button_class, position):
    button_class = button_class.lower().replace(" ", "-") + "-btn"
    orders_container = context.driver.find_element(By.ID, "ordersContainer")
    orders = orders_container.find_elements(By.CLASS_NAME, "order")

    if position not in position_mapping:
        raise ValueError(f"Unsupported position '{position}'")

    order_index = position_mapping[position]

    if order_index >= len(orders):
        raise AssertionError(
            f"There are only {len(orders)} orders, but tried to access the {position} order."
        )

    order_to_click = orders[order_index]

    target_button = order_to_click.find_element(By.CLASS_NAME, button_class)
    target_button.click()


@then('I should see "{expected_value}" in the "{field_name}" field')
def step_impl(context, expected_value, field_name):
    field_value = None
    if field_name == "Customer Name":
        modal = context.driver.find_element(By.ID, "orderModal")
        field_value = modal.find_element(By.ID, "customerInput").get_attribute("value")
    elif field_name == "Status":
        modal = context.driver.find_element(By.ID, "orderModal")
        field_value = modal.find_element(By.ID, "statusInput").get_attribute("value")
    elif field_name == "Item Name":
        modal = context.driver.find_element(By.ID, "itemModal")
        field_value = modal.find_element(By.ID, "itemNameInput").get_attribute("value")
    elif field_name == "Quantity":
        modal = context.driver.find_element(By.ID, "itemModal")
        field_value = modal.find_element(By.ID, "itemQuantityInput").get_attribute(
            "value"
        )
    elif field_name == "Price":
        modal = context.driver.find_element(By.ID, "itemModal")
        field_value = modal.find_element(By.ID, "itemPriceInput").get_attribute("value")
    assert (
        expected_value == field_value
    ), f"Expected to see '{expected_value}' in the '{field_name}' field, but found '{field_value}'."


@when('I set the "{field_name}" to "{new_value}"')
def step_impl(context, field_name, new_value):

    if field_name == "Customer Name":
        modal = context.driver.find_element(By.ID, "orderModal")
        customer_input = modal.find_element(By.ID, "customerInput")
        customer_input.clear()
        customer_input.send_keys(new_value)

    elif field_name == "Status":
        modal = context.driver.find_element(By.ID, "orderModal")
        status_input = modal.find_element(By.ID, "statusInput")
        for option in status_input.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == new_value:
                option.click()
                break
        else:
            raise ValueError(f"Status '{new_value}' not found in dropdown.")

    elif field_name == "Price":
        modal = context.driver.find_element(By.ID, "itemModal")
        price_input = modal.find_element(By.ID, "itemPriceInput")
        price_input.clear()
        price_input.send_keys(new_value)

    elif field_name == "filter-customer-name":
        modal = context.driver.find_element(By.ID, "filterModal")
        filter_customer_name = modal.find_element(By.ID, "filter-customer-name")
        filter_customer_name.clear()
        filter_customer_name.send_keys(new_value)
    elif field_name == "filter-order-status":
        modal = context.driver.find_element(By.ID, "filterModal")
        filter_order_status = modal.find_element(By.ID, "filter-order-status")
        filter_order_status.clear()
        filter_order_status.send_keys(new_value)

    elif field_name == "filter-product-name":
        modal = context.driver.find_element(By.ID, "filterModal")
        filter_product_name = modal.find_element(By.ID, "filter-product-name")
        filter_product_name.clear()
        filter_product_name.send_keys(new_value)

    else:
        raise ValueError(f"Field '{field_name}' not supported.")

    print(f"Successfully set '{field_name}' to '{new_value}'.")


@when('I clear the "{field_name}" field')
def step_impl(context, field_name):
    modal = context.driver.find_element(By.ID, "filterModal")
    field = modal.find_element(By.ID, field_name)
    field.clear()


@then('I should see "{expected_count}" items in the "{position}" Order')
def step_impl(context, expected_count, position):
    orders_container = context.driver.find_element(By.ID, "ordersContainer")
    orders = orders_container.find_elements(By.CLASS_NAME, "order")

    if position not in position_mapping:
        raise ValueError(f"Unsupported position '{position}'")

    order_index = position_mapping[position]

    if order_index >= len(orders):
        raise AssertionError(
            f"There are only {len(orders)} orders, but tried to access the {position} order."
        )

    target_order = orders[order_index]
    item_list = target_order.find_element(By.CLASS_NAME, "item-list")
    items = item_list.find_elements(By.CLASS_NAME, "item")

    actual_count = len(items)
    assert actual_count == int(
        expected_count
    ), f"Expected to see {expected_count} items, but found {actual_count}."


@when('I press the "{item_position}" item in the "{order_position}" Order')
def step_impl(context, item_position, order_position):
    orders_container = context.driver.find_element(By.ID, "ordersContainer")
    orders = orders_container.find_elements(By.CLASS_NAME, "order")

    if order_position not in position_mapping:
        raise ValueError(f"Unsupported order position '{order_position}'")
    order_index = position_mapping[order_position]

    if order_index >= len(orders):
        raise AssertionError(
            f"There are only {len(orders)} orders, but tried to access the {order_position} order."
        )

    target_order = orders[order_index]
    item_list = target_order.find_element(By.CLASS_NAME, "item-list")
    items = item_list.find_elements(By.CLASS_NAME, "item")

    if item_position not in position_mapping:
        raise ValueError(f"Unsupported item position '{item_position}'")
    item_index = position_mapping[item_position]

    if item_index >= len(items):
        raise AssertionError(
            f"There are only {len(items)} items, but tried to access the {item_position} item."
        )

    target_item = items[item_index]
    target_item.click()
