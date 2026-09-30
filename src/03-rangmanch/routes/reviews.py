from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func
from fastapi import Depends  # used for dependency injection (e.g. DB session)
from models import Review, ReviewCreate, ReviewRead, ReviewUpdate  # SQLModel schemas
from database import get_session  # yields a DB session per request

# all routes in this file are prefixed with /reviews and grouped under "reviews" in Swagger docs
router = APIRouter(prefix="/reviews", tags=["reviews"])


# POST /reviews/ — creates a new review; response is shaped by ReviewRead schema
@router.post("/", response_model=ReviewRead)
async def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    """
    Create a new review.
    """
    db_review = Review(
        **review.model_dump()
    )  # convert request body to ORM model instance
    # session.add() registers the object with the session's identity map (Unit of Work pattern);
    # commit() doesn't know what to write unless objects are tracked first via add().
    # This separation also lets you add() multiple objects and commit them all in one transaction.

    session.add(db_review)  # track this object so the session knows to INSERT it

    session.commit()  # flush all tracked changes to the DB in one transaction

    session.refresh(
        db_review
    )  # reload from DB so auto-generated fields (e.g. id) are populated

    return db_review


@router.get("/", response_model=list[ReviewRead])
async def list_reviews(
    play_name: str | None = None,  # optional query parameter to filter by play name
    skip: int = (
        Query(0, ge=0)
    ),  # optional query parameter to skip N records (pagination)
    limit: int = (
        Query(100, ge=1, le=50)
    ),  # optional query parameter to limit N records (pagination)
    session: Session = Depends(get_session),
):
    """
    Retrieve all reviews.
    """
    query = select(Review)
    if play_name:
        query = query.where(Review.play_name == play_name)
    query = query.offset(skip).limit(limit)
    result = session.exec(query)
    return result.all()


@router.get("/average/{play_name}", response_model=ReviewRead)
async def average_review(play_name: str, session: Session = Depends(get_session)):
    """
    Retrieve the average review for a specific play.
    """
    result = session.exec(
        select(func.avg(Review.rating), func.count(Review.rating)).where(
            Review.play_name == play_name
        )
    ).first()
    avg_rating, total_reviews = result

    if total_reviews == 0:
        raise HTTPException(status_code=404, detail="No reviews found for this play")
    return {"play_name": play_name, "rating": avg_rating, "count": total_reviews}


@router.get("/{review_id}", response_model=int)
async def get_review(review_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a specific review by its ID.
    """
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review.id


@router.patch("/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: int, update: ReviewCreate, session: Session = Depends(get_session)
):
    """
    Update a specific review by its ID.
    """
    db_review = session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    for key, value in update.model_dump().items():
        setattr(db_review, key, value)
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review
