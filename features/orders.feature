Feature: The order service back-end
    As an Order Service Manager
    I need a RESTful order service
    So that I can keep track of all orders

Background:
    Given the following orders
        | customer_name | status    | product_name | quantity | price |
        | John Doe     | CREATED   | Device       | 2        | 499.99|
        | Jane Smith   | SHIPPED   | Book         | 1        | 29.99 |
        | Bob Wilson   | CANCELLED | Laptop       | 1        | 999.99|

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Customer Name" to "Alice Brown"
    And I select "CREATED" in the "Status" dropdown 
    And I set the "Product Name" to "Phone"
    And I set the "Quantity" to "1"
    And I set the "Price" to "699.99"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Customer Name" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Alice Brown" in the "Customer Name" field
    And I should see "CREATED" in the "Status" dropdown
    And I should see "Phone" in the "Product Name" field
    And I should see "1" in the "Quantity" field 
    And I should see "699.99" in the "Price" field

Scenario: List all orders 
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "John Doe" in the results
    And I should see "Jane Smith" in the results
    And I should see "Bob Wilson" in the results

Scenario: Search by customer name
    When I visit the "Home Page"
    And I set the "Customer Name" to "John Doe"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "John Doe" in the results
    And I should not see "Jane Smith" in the results
    And I should not see "Bob Wilson" in the results

Scenario: Search by status
    When I visit the "Home Page"
    And I select "SHIPPED" in the "Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jane Smith" in the results
    And I should not see "John Doe" in the results
    And I should not see "Bob Wilson" in the results

Scenario: Cancel an Order
    When I visit the "Home Page"
    And I set the "Customer Name" to "John Doe"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "John Doe" in the "Customer Name" field
    And I should see "CREATED" in the "Status" dropdown
    When I press the "Cancel" button
    Then I should see the message "Success"
    And I should see "CANCELLED" in the "Status" dropdown

Scenario: Update an Order
    When I visit the "Home Page"
    And I set the "Customer Name" to "John Doe"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "John Doe" in the "Customer Name" field
    When I change "Customer Name" to "John Smith"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "John Smith" in the "Customer Name" field