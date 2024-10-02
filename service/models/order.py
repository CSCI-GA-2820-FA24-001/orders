import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .item import Item

logger = logging.getLogger("flask.app")


class Order(db.Model, PersistentBase):
    """Class that represents an Order"""

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="pending")  # 订单状态
    items = db.relationship("ItemModel", backref="order", passive_deletes=True)

    def __repr__(self):
        return f"<OrderModel id={self.id} by {self.customer_name}>"

    def serialize(self):
        """Converts an Order into a dictionary"""
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "items": [item.serialize() for item in self.items],
        }

    def deserialize(self, data):
        """Populates an Order from a dictionary"""
        try:
            self.customer_name = data["customer_name"]
            self.status = data["status"]
            item_list = data.get("items", [])
            for item_data in item_list:
                item = Item()
                item.deserialize(item_data)
                self.items.append(item)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data " + str(error)
            ) from error

        return self
