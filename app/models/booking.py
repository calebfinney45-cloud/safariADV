"""
app/models/booking.py — the Booking table.

Links a User (or a guest, via guest_name/guest_email/guest_phone when
user_id is null) to a TripPackage.

Two independent status fields:
  status         : pending -> confirmed -> completed (or -> cancelled)
  payment_status : unpaid -> paid/failed -> refunded

They're separate because a booking can be confirmed while still unpaid.
"""

from datetime import datetime, timezone

from app.extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    trip_package_id = db.Column(
        db.Integer,
        db.ForeignKey("trip_packages.id"),
        nullable=False,
    )

    # Guest information
    # Used when user_id is null.
    guest_name = db.Column(
        db.String(120),
        nullable=True,
    )

    guest_email = db.Column(
        db.String(255),
        nullable=True,
    )

    guest_phone = db.Column(
        db.String(30),
        nullable=True,
    )

    seats = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    total_price = db.Column(
        db.Numeric(10, 2),
        nullable=False,
    )

    # pending | confirmed | completed | cancelled
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
    )

    # unpaid | paid | failed | refunded
    payment_status = db.Column(
        db.String(20),
        nullable=False,
        default="unpaid",
    )

    notes = db.Column(
        db.Text,
        nullable=True,
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

    # ---------------------------------------------------------
    # User relationship
    # ---------------------------------------------------------
    #
    # User already has:
    #
    # bookings = db.relationship(
    #     "Booking",
    #     backref="traveler",
    #     lazy="dynamic"
    # )
    #
    # Therefore we keep the existing traveler relationship and
    # add user with overlaps to avoid a SQLAlchemy warning.
    # ---------------------------------------------------------

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        overlaps="bookings,traveler",
    )

    # ---------------------------------------------------------
    # Contact helpers
    # ---------------------------------------------------------

    def contact_name(self):
        if self.user_id and self.traveler:
            return self.traveler.name

        return self.guest_name

    def contact_email(self):
        if self.user_id and self.traveler:
            return self.traveler.email

        return self.guest_email

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,

            "user_id": self.user_id,

            "trip_package_id": self.trip_package_id,

            "trip_package": (
                self.trip_package.to_dict(include_agent=False)
                if self.trip_package
                else None
            ),

            "guest_name": self.guest_name,
            "guest_email": self.guest_email,
            "guest_phone": self.guest_phone,

            "contact_name": self.contact_name(),
            "contact_email": self.contact_email(),

            "seats": self.seats,

            "total_price": (
                float(self.total_price)
                if self.total_price is not None
                else None
            ),

            "status": self.status,

            "payment_status": self.payment_status,

            "notes": self.notes,

            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return (
            f"<Booking {self.id} "
            f"trip={self.trip_package_id} "
            f"status={self.status}>"
        )