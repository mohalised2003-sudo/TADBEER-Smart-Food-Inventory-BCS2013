# Data structures for the TADBEER food management system.

from datetime import datetime, timezone
import math


class FoodItem:
    """A food batch with a shelf-life measured from the time it was added."""

    FULL_PRICE_ABOVE = 3.0
    EARLY_DISCOUNT_ABOVE = 2.0
    FLASH_SALE_FROM = 1.0
    MINIMUM_PRICE_RATE = 0.70

    def __init__(self, name, quantity, original_price, time_left,
                 created_at=None, waste_recorded=False):
        self.original_name = name
        self.name = name
        self.quantity = quantity
        self.original_price = original_price
        self.current_price = original_price
        self.initial_time_left = float(time_left)
        self.time_left = float(time_left)
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.status = "Safe (Full Price)"
        self.discount_rate = 0.0
        self.waste_recorded = waste_recorded

    def refresh_time_left(self, time_unit):
        """Decrease the entered shelf-life by elapsed wall-clock time."""
        created = datetime.fromisoformat(self.created_at)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        elapsed_hours = max(0.0, (datetime.now(timezone.utc) - created).total_seconds() / 3600)
        elapsed = elapsed_hours if time_unit == "hours" else elapsed_hours / 24
        self.time_left = max(0.0, self.initial_time_left - elapsed)
        self.update_status()

    def update_status(self):
        """Apply staged discounts while keeping at least 70% of list price."""
        if not math.isfinite(self.time_left) or self.time_left <= 0:
            self.name = self.original_name
            self.status = "Waste (Expired)"
            self.current_price = 0.0
            self.discount_rate = 0.0
        elif self.time_left > self.FULL_PRICE_ABOVE:
            self.name = self.original_name
            self.status = "Safe (Full Price)"
            self.current_price = self.original_price
            self.discount_rate = 0.0
        elif self.time_left > self.EARLY_DISCOUNT_ABOVE:
            self.name = self.original_name
            self.status = "Early Discount (15% Off)"
            self.discount_rate = 0.15
            self.current_price = self._discounted_price()
        elif self.time_left >= self.FLASH_SALE_FROM:
            self.name = f"Mystery Box ({self.original_name[:3].upper()}*)"
            self.status = "Flash Sale (30% Off)"
            self.discount_rate = 0.30
            self.current_price = self._discounted_price()
        else:
            self.name = self.original_name
            self.status = "Urgent Donation"
            self.current_price = 0.0
            self.discount_rate = 0.0

    def _discounted_price(self):
        """Round to cents without crossing the seller's minimum price floor."""
        discounted = round(self.original_price * (1 - self.discount_rate), 2)
        minimum = math.ceil(self.original_price * self.MINIMUM_PRICE_RATE * 100 - 1e-9) / 100
        return min(self.original_price, max(discounted, minimum))

    def to_dict(self):
        return {
            "original_name": self.original_name,
            "quantity": self.quantity,
            "original_price": self.original_price,
            "initial_time_left": self.initial_time_left,
            "created_at": self.created_at,
            "waste_recorded": self.waste_recorded,
        }

    @classmethod
    def from_dict(cls, data):
        item = cls(
            data["original_name"], data["quantity"], data["original_price"],
            data["initial_time_left"], data.get("created_at"),
            data.get("waste_recorded", False),
        )
        item.update_status()
        return item
