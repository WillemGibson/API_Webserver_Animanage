from flask import Blueprint, request

from init import db
from models.reviews import Review, reviews_schema, review_schema
from models.genres import Genre, genres_schema, genre_schema
from flask_jwt_extended import jwt_required, get_jwt_identity

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

# http://localhost:8080/reviews - GET
@reviews_bp.route('/')
@jwt_required()
def get_all_reviews():
    stmt = db.select(Review).order_by(Review.title.asc())
    reviews = db.session.scalars(stmt)

    return reviews_schema.dump(reviews)

# http://localhost:8080/reviews/id - GET
@reviews_bp.route('/<int:review_id>')
@jwt_required()
def get_one_review(review_id): # review_id = 4
    stmt = db.select(Review).filter_by(id=review_id) # SELECT * FROM reviews WHERE id=4
    review = db.session.scalar(stmt)

    if review:
        return review_schema.dump(review)
    else:
        return {"error": f"Review {review_id} does not exist"}
    
# http://localhost:8080/reviews - POST
@reviews_bp.route('/', methods=['POST'])
@jwt_required()
def create_review():
    body_data = request.get_json()
    # Create a new review model instance
    review = Review(
        user_id = get_jwt_identity(),
        title = body_data.get('title'),
        status_id = body_data.get('status_id'),
        type_id = body_data.get('type_id'),
        rating_id = body_data.get('rating_id'),
        # genre
        eps_watched = body_data.get('eps_watched'),
        eps_total = body_data.get('eps_total'),
        date_started = body_data.get('date_started'),
        date_finished = body_data.get('date_finished'),
        recom = body_data.get('recom'),
        fav = body_data.get('fav'),
        com = body_data.get('com')
    )
    # Add that to the session and commit
    db.session.add(review)
    db.session.commit()
    # return the newly created review
    return review_schema.dump(review), 201

# https://localhost:8080/reviews/6 - DELETE
@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    # get the review from the db with id = review_id
    stmt = db.select(Review).where(Review.id == review_id)
    review = db.session.scalar(stmt)
    # if review exists:
    if review:
        # delete the review from the session and commit
        db.session.delete(review)
        db.session.commit()
        # return messsage
        return {'Message': f"Review {review.title} was deleted"}
    # else
    else:
        # return error message
        return {'Error': f"Review {review_id} not found"}, 404
    pass

# https://localhost:8080/reviews/6 - PUT or PATCH
@reviews_bp.route('/<int:review_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_review(review_id):
    # Get the data to be updated form the body of the request
    body_data = request.get_json()
    # Get the review from the db whose fields need to be updated
    stmt = db.select(Review).filter_by(id=review_id)
    review = db.session.scalar(stmt)
    # if review exists
    if review:
        # update the fields
        review.title = body_data.get('title') or review.title
        review.status_id = body_data.get('status_id') or review.status_id
        review.type_id = body_data.get('type_id') or review.type_id
        review.rating_id = body_data.get('rating_id') or review.rating_id
        # genre
        review.eps_watched = body_data.get('eps_watched') or review.eps_watched
        review.eps_total = body_data.get('eps_total') or review.eps_total
        review.date_started = body_data.get('date_started') or review.date_started
        review.date_finished = body_data.get('date_finished') or review.date_finished
        review.recom = body_data.get('recom') or review.recom
        review.fav = body_data.get('fav') or review.fav
        review.com = body_data.get('com') or review.com
        # commit the changes
        db.session.commit()
        # return updated review
        return review_schema.dump(review)
    # else
    else:
        # return error message
        return {"Error": f"Review {review_id} not found"}, 404

# Genre Endpoints
    
# https://localhost:8080/reviews/6/genres/ - GET
# @reviews_bp.route('/<int:review_id>/genres')
# def check_genres(review_id): # review_id = 4
#     stmt = db.select(Genre).filter_by(genres_id) # SELECT * FROM reviews WHERE id=4
#     review = db.session.scalar(stmt)

#     if review:
#         return review_schema.dump(review)
#     else:
#         return {"error": f"Review {review_id} does not have any genres"}
    
# https://localhost:8080/reviews/6/genres/10 - POST
@reviews_bp.route('/<int:review_id>/genres/<int:genre_id>', methods=['POST'])
@jwt_required()
def link_genre_to_review(review_id, genre_id):
    # Get the data to be updated form the body of the request
    body_data = request.get_json()
    # get the review & genre from their respected db whose fields need to be updated
    stmt1 = db.select(Review).filter_by(id=review_id)
    stmt2 = db.select(Genre).filter_by(id=genre_id)

    review = db.session.scalar(stmt1)
    genre = db.session.scalar(stmt2)

    # if review exists
    if review:
        # update the fields
        review.genres.append(genre)
        # commit the changes
        db.session.commit()
        # return updated review
        return review_schema.dump(review)
    # else
    else:
        # return error message
        return {"Error": f"Genre {genre_id} could not connect to {review_id}"}, 404
    
# https://localhost:8080/reviews/6/genres/10 - DELETE
@reviews_bp.route('/<int:review_id>/genres/<int:genre_id>', methods=['DELETE'])
@jwt_required()
def delete_linked_genre(review_id, genre_id):
    # get the review & genre from their respected db with id = review_id
    stmt1 = db.select(Review).where(Review.id == review_id)
    stmt2 = db.select(Genre).where(Genre.id == genre_id)

    review = db.session.scalar(stmt1)
    genre = db.session.scalar(stmt2)
    # if review exists
    if review:
        # update the fields
        review.genres.remove(genre)
        # commit the changes
        db.session.commit()
        # return updated review
        return review_schema.dump(review)
    # else
    else:
        # return error message
        return {"Error": f"Genre {genre_id} could not connect to {review_id}"}, 404