
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, jsonify

from app.extensions import db
from app.models.favorite import Favorite
from app.models.trip_package import TripPackage
from app.utils.decorators import role_required

favorites_bp = Blueprint("favorites", __name__, url_prefix="/api/favorites")


@favorites_bp.route("", methods=["GET"])
@role_required("traveler")
def list_favorites(current_user):
    """Return the current traveler's favorite trip packages."""
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()

    trips = []
    for favorite in favorites:
        trip = TripPackage.query.get(favorite.trip_package_id)
        if trip:
            trips.append(trip.to_dict())

    return jsonify(trips), 200


@favorites_bp.route("/<int:trip_id>", methods=["POST"])
@role_required("traveler")
def add_favorite(current_user, trip_id):
    trip = TripPackage.query.get(trip_id)

    if not trip:
        return jsonify({"error": "Trip package not found."}), 404

    favorite = Favorite(
        user_id=current_user.id,
        trip_package_id=trip_id,
    )

    db.session.add(favorite)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(
            {"error": "This trip is already in your favorites."}
        ), 409

    return jsonify(favorite.to_dict()), 201


@favorites_bp.route("/<int:trip_id>", methods=["DELETE"])
@role_required("traveler")
def remove_favorite(current_user, trip_id):
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        trip_package_id=trip_id,
    ).first()

    if not favorite:
        return jsonify(
            {"error": "This trip is not in your favorites."}
        ), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Removed from favorites."}), 200