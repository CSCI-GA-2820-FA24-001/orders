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

Scenario: List all Orders
    When I visit the "Home Page"
    Then I should see "3" orders

Scenario: Create an Order
    When I visit the "Home Page"
    And I press the "New Order" button
    Then I should see "4" orders

Scenario: Delete an Order
    When I visit the "Home Page"
    And I press the "Delete Order" button for the "First" order
    Then I should see "2" orders

Scenario: Update an Order
    When I visit the "Home Page"
    Then I should see "3" orders
    When I press the "Order Info" button for the "First" order
    Then I should see "John Doe" in the "Customer Name" field
    When I set the "Customer Name" to "Jane Doe"
    And I press the "Save Order" button
    When I press the "Order Info" button for the "First" order
    Then I should see "Jane Doe" in the "Customer Name" field

Scenario: Cancel an Order
    When I visit the "Home Page"
    Then I should see "3" orders
    When I press the "Order Info" button for the "First" order
    Then I should see "CREATED" in the "Status" field
    When I set the "Status" to "CANCELLED"
    And I press the "Save Order" button
    When I press the "Order Info" button for the "First" Order
    Then I should see "CANCELLED" in the "Status" field


Scenario: Create an Item
    When I visit the "Home Page"
    And I press the "Add Item" button for the "First" order
    Then I should see "2" items in the "First" order

Scenario: Read an Item
    When I visit the "Home Page"
    Then I should see "3" orders
    When I press the "First" item in the "First" order
    Then I should see "Device" in the "Item Name" field 
    And I should see "2" in the "Quantity" field
    And I should see "499.99" in the "Price" field

Scenario: Delete an Item
    When I visit the "Home Page"
    And I press the "Add Item" button for the "First" order
    Then I should see "2" items in the "First" order
    When I press the "First" item in the "First" order
    Then I should see "Device" in the "Item Name" field 
    When I press the "Delete Item" button
    Then I should see "1" items in the "First" order


Scenario: Update an Item
    When I visit the "Home Page"
    When I press the "First" item in the "First" order
    Then I should see "Device" in the "Item Name" field 
    When I set the "Price" to "600.00"
    And I press the "Save Item" button
    When I press the "First" item in the "First" order
    Then I should see "600" in the "Price" field


Scenario: Query Orders by Various Criteria
    When I visit the "Home Page"

    # Test filtering by Order Customer Name
    When I set the "filter-customer-name" to "John Doe"
    And I press the "Filter" button
    Then I should see "1" orders
    
    # Test filtering by Order Status
    When I clear the "filter-customer-name" field
    And I press the "Filter" button
    Then I should see "3" orders
    When I set the "filter-order-status" to "SHIPPED"
    And I press the "Filter" button
    Then I should see "1" orders

    
    # Test filtering by Order Product Name
    When I clear the "filter-order-status" field
    And I press the "Filter" button
    Then I should see "3" orders
    When I set the "filter-product-name" to "Laptop"
    And I press the "Filter" button
    Then I should see "1" orders
    
    # Test combined filters
    When I clear the "filter-product-name" field
    And I press the "Filter" button
    Then I should see "3" orders
    When I set the "filter-product-name" to "Laptop"
    And I set the "filter-customer-name" to "Bob Wilson"
    And I press the "Filter" button
    Then I should see "1" orders