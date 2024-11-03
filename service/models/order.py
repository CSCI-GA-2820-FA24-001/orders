import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .item import Item
from enum import Enum

logger = logging.getLogger("flask.app")

class Order_Status(Enum):
    """Enumeration of valid order statuses"""

    Created = 'Created'
    In_Progress = 'In_Progress'
    Shipped = 'Shipped'
    Completed = 'Completed'


class Order(db.Model, PersistentBase):
    """Class that represents an Order"""

    # Table Schema

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Enum(Order_Status), default=Order_Status.Created, nullable=False)
    items = db.relationship("Item", backref="order", passive_deletes=True)

    def __repr__(self):
        return f"<Order id={self.id} by {self.customer_name}>"

    def serialize(self):
        """Converts an Order into a dictionary"""
        if not isinstance(self.status, Order_Status):
            raise DataValidationError(f"Invalid status value '{self.status}' not in Order_Status Enum")
        
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "items": [item.serialize() for item in self.items],
        }

    def deserialize(self, data):
        """Populates an Order from a dictionary"""
        try:
            self.customer_name = data["customer_name"]
            try:
                self.status = Order_Status(data["status"])
            except ValueError:
                raise DataValidationError(f"Invalid status value '{data['status']}' not in Order_Status Enum")
            item_list = data.get("items", [])
            for item_data in item_list:
                item = Item()
                item.deserialize(item_data)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data " + str(error)
            ) from error

        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns all Orders with the given customer name
        Args:
            name (string): the name of the customer whose orders you want
        """
        logger.info("Processing customer name query for %s ...", name)
        return cls.query.filter(cls.customer_name == name)
