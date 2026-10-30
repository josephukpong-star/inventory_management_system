import math
from datetime import datetime
_DATE_NOT_PROVIDED = object()

class Product:
    def __init__(
        self,
        product_id,
        name,
        price,
        quantity,
        category="Uncategorized",
        base_unit="unit",
        purchase_units=None,
        selling_units=None,
        selling_price=None,
        date_added=_DATE_NOT_PROVIDED,
    ):
        if isinstance(product_id, bool) or not isinstance(product_id, int):
            raise ValueError("Product ID must be an integer")
        if product_id <= 0:
            raise ValueError("Product ID must be greater than zero")

        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")

        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise ValueError("Price must be a number")
        if not math.isfinite(price):
            raise ValueError("Price must be finite")
        if price < 0:
            raise ValueError("Price cannot be negative")

        if selling_price is None:
            selling_price = price

        if isinstance(selling_price, bool) or not isinstance(
            selling_price, (int, float)
        ):
            raise ValueError("Selling price must be a number")
        if not math.isfinite(selling_price):
            raise ValueError("Selling price must be finite")
        if selling_price < 0:
            raise ValueError("Selling price cannot be negative")

        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Quantity must be an integer")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        if not category or not category.strip():
            raise ValueError("Category cannot be empty")

        if not isinstance(base_unit, str) or not base_unit.strip():
            raise ValueError("Base unit cannot be empty")

        self._validate_units(purchase_units, "Purchase")
        self._validate_units(selling_units, "Selling")

        self.product_id = product_id
        self.name = name.strip().title()
        self.price = price
        self.selling_price = selling_price
        self.quantity = quantity
        self.category = category.strip().title()
        self.base_unit = base_unit.strip().lower()
        self.purchase_units = self._normalize_units(purchase_units)
        self.selling_units = self._normalize_units(selling_units)

        # Record the creation date for new products.
        # Preserve the original date when loading an existing product.
        if date_added is _DATE_NOT_PROVIDED:
            self.date_added = datetime.now().date().isoformat()
        else:
            self.date_added = date_added

    @staticmethod
    def _validate_units(units, unit_type):
        if units is None:
            return

        if not isinstance(units, list):
            raise ValueError(f"{unit_type} units must be a list")

        seen_names = set()

        for unit in units:
            if not isinstance(unit, dict):
                raise ValueError(
                    f"Each {unit_type.lower()} unit must be a dictionary"
                )

            name = unit.get("name")
            factor = unit.get("base_quantity")

            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"{unit_type} unit name cannot be empty")

            normalized_name = name.strip().lower()

            if normalized_name in seen_names:
                raise ValueError(f"Duplicate {unit_type.lower()} unit name")

            seen_names.add(normalized_name)

            if isinstance(factor, bool) or not isinstance(factor, (int, float)):
                raise ValueError(
                    f"{unit_type} unit conversion factor must be a number"
                )

            if not math.isfinite(factor):
                raise ValueError(
                    f"{unit_type} unit conversion factor must be finite"
                )

            if factor <= 0:
                raise ValueError(
                    f"{unit_type} unit conversion factor must be greater than zero"
                )

    @staticmethod
    def _normalize_units(units):
        if units is None:
            return []

        return [
            {
                "name": unit["name"].strip().lower(),
                "base_quantity": unit["base_quantity"],
            }
            for unit in units
        ]

    def to_dict(self):
        data = {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "category": self.category,
            "date_added": self.date_added,
        }

        # Save selling_price only when it differs from the existing cost price.
        if self.selling_price != self.price:
            data["selling_price"] = self.selling_price

        # Preserve the existing JSON structure for legacy products.
        if (
            self.base_unit != "unit"
            or self.purchase_units
            or self.selling_units
        ):
            data["base_unit"] = self.base_unit
            data["purchase_units"] = self.purchase_units
            data["selling_units"] = self.selling_units

        return data