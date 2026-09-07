from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.booking import Booking
from app.models.review import Review
from app.models.trip_package import TripPackage


reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.get("/api/trip_packages/<int:trip_package_id>/reviews")
def get_reviews(trip_package_id):
    trip_package = TripPackage.query.get(trip_package_id)

    if not trip_package:
        return jsonify({"error": "Trip package not found."}), 404

    reviews = (
        Review.query
        .filter_by(trip_package_id=trip_package_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return jsonify({
        "reviews": [review.to_dict() for review in reviews],
        "count": len(reviews),
    }), 200


@reviews_bp.post("/api/bookings/<int:booking_id>/review")
@jwt_required()
def create_review(booking_id):
    current_user_id = get_jwt_identity()

    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity."}), 401

    booking = Booking.query.get(booking_id)

    if not booking:
        return jsonify({"error": "Booking not found."}), 404

    # 1. The booking must belong to the logged-in user.
    if booking.user_id != current_user_id:
        return jsonify({
            "error": "You can only review your own booking."
        }), 403

    # 2. The trip must have been completed.
    if booking.status != "completed":
        return jsonify({
            "error": "You can only review a completed trip."
        }), 400

    # 3. One review per booking.
    existing_review = Review.query.filter_by(
        booking_id=booking.id
    ).first()

    if existing_review:
        return jsonify({
            "error": "This booking has already been reviewed."
        }), 409

    data = request.get_json(silent=True) or {}

    rating = data.get("rating")
    comment = data.get("comment")

    # Rating must be an integer from 1 to 5.
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({
            "error": "Rating must be a number from 1 to 5."
        }), 400

    if rating < 1 or rating > 5:
        return jsonify({
            "error": "Rating must be between 1 and 5."
        }), 400

    # Use guest name first, otherwise the logged-in user's name.
    reviewer_name = (
        booking.guest_name
        or (booking.user.name if booking.user else "Traveler")
    )

    review = Review(
        booking_id=booking.id,
        trip_package_id=booking.trip_package_id,
        user_id=booking.user_id,
        rating=rating,
        comment=comment,
        reviewer_name=reviewer_name,
    )

    db.session.add(review)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Unable to create review."
        }), 500

    return jsonify({
        "message": "Review submitted successfully.",
        "review": review.to_dict(),
    }), 201