from datetime import datetime, timezone

from app.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        nullable=False,
        unique=True,
    )

    trip_package_id = db.Column(
        db.Integer,
        db.ForeignKey("trip_packages.id"),
        nullable=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    rating = db.Column(db.Integer, nullable=False)

    comment = db.Column(db.Text, nullable=True)

    reviewer_name = db.Column(db.String(120), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    booking = db.relationship(
        "Booking",
        backref="review",
        lazy=True,
    )

    trip_package = db.relationship(
        "TripPackage",
        back_populates="reviews",
        lazy=True,
    )

    user = db.relationship(
        "User",
        lazy=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "trip_package_id": self.trip_package_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "comment": self.comment,
            "reviewer_name": self.reviewer_name,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return f"<Review {self.id} trip={self.trip_package_id} rating={self.rating}>"