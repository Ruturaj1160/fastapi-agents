from fastapi import APIRouter, Depends, Query
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
