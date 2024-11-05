import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .item import Item
from enum import Enum

logger = logging.getLogger("flask.app")


class Order_Status(Enum):
    """Enumeration of valid order statuses"""

    CREATED = 'CREATED'
    IN_PROGRESS = 'IN_PROGRESS'
    SHIPPED = 'SHIPPED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

    @staticmethod
    def list():
        return list(map(lambda s: s.value, Order_Status))


class Order(db.Model, PersistentBase):
    """Class that represents an Order"""

    # Table Schema

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Enum(Order_Status), default=Order_Status.CREATED, nullable=False)
    items = db.relationship("Item", backref="order", passive_deletes=True)

    def __repr__(self):
        return f"<Order id={self.id} by {self.customer_name}>"

    def serialize(self):
        """Converts an Order into a dictionary"""
        if not isinstance(self.status, Order_Status):
            raise DataValidationError(
                f"Invalid status value '{self.status}' not in Order_Status Enum"
            )

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
                self.status = Order_Status(data["status"].upper())
            except ValueError:
                raise DataValidationError(f"Invalid status value '{data['status'].upper()}' not in Order_Status Enum")

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
    def find_by_filters(cls, customer_name=None, order_status=None, product_name=None):
        """Returns all Orders with the given filters
        Args:
            customer_name (string): the name of the customer whose orders you want
            status (string): the status of orders you want
            product_name (string): the product_name of orders you want
        """
        query = cls.query
        if customer_name:
            query = query.filter(cls.customer_name == customer_name)
        if order_status:
            if order_status in Order_Status.list():
                query = query.filter(cls.status == Order_Status[order_status])
            else:
                query = query.filter(False)
        if product_name:
            query = query.join(Item).filter(Item.product_name == product_name)
        return query.all()
