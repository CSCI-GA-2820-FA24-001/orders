"""
Properties and functions for Item
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


class Item(db.Model, PersistentBase):
    """Class that represents an Item"""

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    product_name = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<Item id={self.id} product_name=[{self.product_name}] order_id={self.order_id} price={self.price}>"

    def serialize(self):
        """Converts an Item into a dictionary"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": self.price,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def deserialize(self, data):
        """Populates an Item from a dictionary"""
        try:
            self.product_name = data["product_name"]
            self.quantity = data["quantity"]
            self.price = data["price"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + str(error)
            ) from error

        return self
