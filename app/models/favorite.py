from datetime import datetime, timezone

from app.extensions import db


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    trip_package_id = db.Column(
        db.Integer,
        db.ForeignKey("trip_packages.id"),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "trip_package_id",
            name="uq_favorite_user_trip",
        ),
    )

    user = db.relationship(
        "User",
        backref="favorites",
        lazy=True,
    )

    trip_package = db.relationship(
        "TripPackage",
        backref="favorites",
        lazy=True,
    )

    def __repr__(self):
        return f"<Favorite user={self.user_id} trip={self.trip_package_id}>"