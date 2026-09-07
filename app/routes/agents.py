from flask import Blueprint, jsonify

from app.models.user import User


agents_bp = Blueprint("agents", __name__)


@agents_bp.get("/api/agents/<int:agent_id>")
def get_agent(agent_id):
    # Find the user
    agent = User.query.get(agent_id)

    # Treat these three cases the same:
    # 1. Agent does not exist
    # 2. User is not an agent
    # 3. Agent account is not active
    if (
        not agent
        or agent.role != "agent"
        or agent.status != "active"
    ):
        return jsonify({
            "error": "Agent not found."
        }), 404

    # Only approved trips are visible publicly.
    trips = [
        trip
        for trip in agent.trip_packages
        if trip.status == "approved"
    ]

    # Collect all reviews from the agent's approved trips.
    all_reviews = [
        review
        for trip in trips
        for review in trip.reviews
    ]

    # Calculate the agent's overall rating.
    if all_reviews:
        average_rating = round(
            sum(review.rating for review in all_reviews)
            / len(all_reviews),
            1,
        )
    else:
        average_rating = None

    return jsonify({
        "id": agent.id,
        "name": agent.name,
        "business_name": agent.business_name,

        "trips": [
            trip.to_dict()
            for trip in trips
        ],

        "average_rating": average_rating,
        "review_count": len(all_reviews),
    }), 200