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
