"""
app/models/trip_package.py — the TripPackage table.

Holds everything about one bookable trip. status moves through:
  pending -> approved -> (rejected | blacklisted)

spots_remaining is computed on the fly from capacity - spots_booked, not
stored — so it's always accurate and never drifts out of sync.

average_rating and review_count are computed from the reviews attached
to this trip package. They are not stored database columns.
"""

from datetime import datetime, timezone

from app.extensions import db
from app.models.category import trip_package_categories


class TripPackage(db.Model):
    __tablename__ = "trip_packages"

    id = db.Column(db.Integer, primary_key=True)

    agent_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    title = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    itinerary = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)

    price = db.Column(db.Numeric(10, 2), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    spots_booked = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    image_url = db.Column(db.Text, nullable=True)

    # pending | approved | rejected | blacklisted
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    categories = db.relationship(
        "Category",
        secondary=trip_package_categories,
        backref="trip_packages",
        lazy="joined",
    )

    bookings = db.relationship(
        "Booking",
        backref="trip_package",
        lazy="dynamic",
    )

    reviews = db.relationship(
        "Review",
        back_populates="trip_package",
        lazy=True,
        cascade="all, delete-orphan",
    )

    @property
    def spots_remaining(self):
        return max(self.capacity - self.spots_booked, 0)

    @property
    def average_rating(self):
        if not self.reviews:
            return None

        return round(
            sum(review.rating for review in self.reviews)
            / len(self.reviews),
            1,
        )

    @property
    def review_count(self):
        return len(self.reviews)

    def to_dict(self, include_agent=True):
        data = {
            "id": self.id,
            "agent_id": self.agent_id,
            "title": self.title,
            "destination": self.destination,
            "itinerary": self.itinerary,
            "description": self.description,
            "price": (
                float(self.price)
                if self.price is not None
                else None
            ),
            "capacity": self.capacity,
            "spots_booked": self.spots_booked,
            "spots_remaining": self.spots_remaining,
            "average_rating": self.average_rating,
            "review_count": self.review_count,
            "start_date": (
                self.start_date.isoformat()
                if self.start_date
                else None
            ),
            "end_date": (
                self.end_date.isoformat()
                if self.end_date
                else None
            ),
            "image_url": self.image_url,
            "status": self.status,
            "categories": [
                category.to_dict()
                for category in self.categories
            ],
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

        if include_agent and self.agent is not None:
            data["agent"] = {
                "id": self.agent.id,
                "name": self.agent.name,
                "business_name": self.agent.business_name,
            }

        return data

    def __repr__(self):
        return (
            f"<TripPackage {self.id} "
            f"{self.title} ({self.status})>"
        )