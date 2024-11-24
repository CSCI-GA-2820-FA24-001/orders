Feature: The order service back-end
    As an Order Service Manager
    I need a RESTful order service
    So that I can keep track of all orders

Background:
    Given the following orders
        | customer_name | status   | product_name | quantity | price   |
        | John Doe     | CREATED   | Device       | 2        | 499.99  |
        | Jane Smith   | SHIPPED   | Book         | 1        | 29.99   |
        | Bob Wilson   | CANCELLED | Laptop       | 1        | 999.99  |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Demo RESTful Service" in the title
    And I should not see "404 Not Found"

# TODO  delete also automatically shows Cancelled order?
Scenario: Delete an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "John Doe" in the "Order Customer Name" field
    And I should see "CREATED" in the "Order Status" field
    And I should see "Device" in the "Order Product Name" field
    And I should see "499.99" in the "Order Price" field
    When I press the "Delete" button
    Then I should see the message "Order has been Deleted!"
    When I press the "Clear" button
    And I press the "Search" button
    Then I should not see the copied "Order ID" in results

Scenario: List all Orders
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jane Smith" in the results
    And I should see "Bob Wilson" in the results

Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Order Customer Name" to "John Doe"
    And I select "CREATED" in the "Order Status" dropdown
    And I set the "Order Product Name" to "Device"
    And I set the "Order Quantity" to "2"
    And I set the "Order Price" to "499.99"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "John Doe" in the "Order Customer Name" field
    And I should see "CREATED" in the "Order Status" field
    And I should see "Device" in the "Order Product Name" field
    And I should see "2" in the "Order Quantity" field 
    And I should see "499.99" in the "Order Price" field

Scenario: Update an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I set the "Order Customer Name" to "Jane Doe"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Jane Doe" in the "Order Customer Name" field

Scenario: Query Orders by Various Criteria
    When I visit the "Home Page"
    And I press the "Clear" button
    # Test filtering by Order Customer Name
    When I set the "Order Customer Name" to "John Doe"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "John Doe" in the results
    And I should not see "Jane Smith" in the results
    And I should not see "Bob Wilson" in the results
    
    # Test filtering by Order Status
    When I press the "Clear" button
    And I select "SHIPPED" in the "Order Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jane Smith" in the results
    And I should not see "John Doe" in the results
    And I should not see "Bob Wilson" in the results
    
    # Test filtering by Order Product Name
    When I press the "Clear" button
    And I set the "Order Product Name" to "Laptop"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Bob Wilson" in the results
    And I should not see "John Doe" in the results
    And I should not see "Jane Smith" in the results
    
    # Test combined filters
    When I press the "Clear" button
    And I set the "Order Customer Name" to "Bob Wilson"
    And I select "CANCELLED" in the "Order Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Bob Wilson" in the results
    And I should see "CANCELLED" in the results
    And I should not see "John Doe" in the results
    And I should not see "Jane Smith" in the results

Scenario: Cancel an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "John Doe" in the "Order Customer Name" field
    And I should see "CREATED" in the "Order Status" field
    When I press the "Cancel" button
    Then I should see the message "Success"
    And I should see "CANCELLED" in the "Order Status" field
    # Verify the order remains cancelled after refresh
    When I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "CANCELLED" in the "Order Status" field

Scenario: Read an Item
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I paste the "Order ID Item" field 
    And I press the "Search Item" button
    Then I should see the message "Success"
    When I leave the "Item Product Name" field empty
    And I leave the "Item Quantity" field empty
    And I leave the "Item Price" field empty
    And I press the "Retrieve Item" button
    Then I should see the message "Success" in the item form
    And I should see "Device" in the "Item Product Name" field
    And I should see "2" in the "Item Quantity" field
    And I should see "499.99" in the "Item Price" field

Scenario: Delete an Item
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I paste the "Order ID Item" field 
    And I press the "Search Item" button
    Then I should see the message "Success"
    And I should see "Device" in the "Item Product Name" field
    And I should see "2" in the "Item Quantity" field
    And I should see "499.99" in the "Item Price" field
    When I copy the "Item ID" field
    And I leave the "Item Product Name" field empty
    And I leave the "Item Quantity" field empty
    And I leave the "Item Price" field empty
    And I press the "Delete Item" button
    Then I should see the message "Item has been Deleted!" in the item form