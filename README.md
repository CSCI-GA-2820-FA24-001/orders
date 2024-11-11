# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
![Build Status](https://github.com/CSCI-GA-2820-FA24-001/orders/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA24-001/orders/graph/badge.svg?token=FDCXWZEHD4)](https://codecov.io/gh/CSCI-GA-2820-FA24-001/orders)

This is a skeleton you can use to start your projects

## Overview

This repository contains code for the Customer Orders microservice for an e-commerce web site. It contains REST API calls to all CRUD operations on orders along with CRUD subordinate resource calls to item in an order.

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── order.py               - module with database model for order
├── item.py                - module with database model for item
├── routes.py              - module with order service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_order.py          - test suite for order db model
├── test_item.py           - test suite for item db model
└── test_routes.py         - test suite for order service routes
```
## Information about this repo
``` These are the RESTful endpoints for orders and items

Endpoint          Methods  Rule
----------------  -------  -----------------------------------------------------
index             GET      /

list_orders       GET      /orders
create_order      POST     /orders
read_order        GET      /orders/<int:order_id>
update_order      PUT      /orders/<int:order_id>
delete_order      DELETE   /orders/<int:order_id>

list_items        GET      /accounts/<int:order_id>/items
create_items      POST     /orders/<int:order_id>/items
get_items         GET      /orders/<int:order_id>/items/<int:item_id>
update_items      PUT      /orders/<int:order_id>/items/<int:item_id>
delete_items      DELETE   /orders/<int:order_id>/items/<int:item_id>
```
### create_order & update_order input JSON format
```
{
  "customer_name": "string",
  "status": "string",
  "items": [
    {
      "product_name": "string",
      "quantity": "int",
      "price": "float"
    },
    ...
  ]
}
```

### create_items & update_items input JSON format
```
{
  "product_name": "string",
  "quantity": "int",
  "price": "float"
}
```

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
