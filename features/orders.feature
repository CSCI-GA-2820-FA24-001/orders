Feature: The order service back-end
    As an Order Service Manager
    I need a RESTful order service
    So that I can keep track of all orders

Background:
    Given the following orders
        | customer_name | status    | product_name | quantity | price   |
        | John Doe     | CREATED   | Device       | 2        | 499.99  |
        | Jane Smith   | SHIPPED   | Book         | 1        | 29.99   |
        | Bob Wilson   | CANCELLED | Laptop       | 1        | 999.99  |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Demo RESTful Service" in the title
    And I should not see "404 Not Found"

# should delete also automatically show Cancelled order
Scenario: Delete an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "John Doe" in the "Customer Name" field
    And I should see "CREATED" in the "Status" field
    And I should see "Device" in the "Product Name" field
    And I should see "499.99" in the "Price" field
    When I press the "Delete" button
    Then I should see the message "Order has been Deleted!"
    When I press the "Clear" button
    And I press the "Search" button
    Then I should not see the copied "ID" in results

Scenario: List all Orders
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jane Smith" in the results
    And I should see "Bob Wilson" in the results

Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Customer Name" to "John Doe"
    And I select "CREATED" in the "Status" dropdown
    And I set the "Product Name" to "Device"
    And I set the "Quantity" to "2"
    And I set the "Price" to "499.99"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "John Doe" in the "Customer Name" field
    And I should see "CREATED" in the "Status" field
    And I should see "Device" in the "Product Name" field
    And I should see "2" in the "Quantity" field 
    And I should see "499.99" in the "Price" field
