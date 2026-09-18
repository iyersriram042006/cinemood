from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Friendship
from app.schemas.social import FriendRequestCreate

router = APIRouter(prefix="/api/friends", tags=["friends"])

@router.post("/request")
def send_request(data: FriendRequestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    addressee = db.query(User).filter(User.email == data.addressee_email).first()
    if not addressee:
        raise HTTPException(status_code=404, detail="User not found")
    if addressee.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot friend yourself")

    existing = db.query(Friendship).filter(
        or_(
            and_(Friendship.requester_id == user.id, Friendship.addressee_id == addressee.id),
            and_(Friendship.requester_id == addressee.id, Friendship.addressee_id == user.id),
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Friendship already {existing.status}")

    friendship = Friendship(requester_id=user.id, addressee_id=addressee.id, status="pending")
    db.add(friendship)
    db.commit()
    db.refresh(friendship)
    return {"message": "Friend request sent", "id": str(friendship.id)}

@router.post("/{friendship_id}/accept")
def accept_request(friendship_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id, Friendship.addressee_id == user.id).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Request not found")
    friendship.status = "accepted"
    db.commit()
    return {"message": "Friend request accepted"}

@router.post("/{friendship_id}/reject")
def reject_request(friendship_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id, Friendship.addressee_id == user.id).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Request not found")
    friendship.status = "rejected"
    db.commit()
    return {"message": "Friend request rejected"}

@router.get("")
def list_friends(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    friendships = db.query(Friendship).filter(
        or_(Friendship.requester_id == user.id, Friendship.addressee_id == user.id),
        Friendship.status == "accepted"
    ).all()

    result = []
    for f in friendships:
        other_id = f.addressee_id if f.requester_id == user.id else f.requester_id
        other = db.query(User).filter(User.id == other_id).first()
        result.append({"id": str(f.id), "status": f.status, "other_user_name": other.name, "other_user_email": other.email})
    return result

@router.get("/pending")
def list_pending(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    friendships = db.query(Friendship).filter(Friendship.addressee_id == user.id, Friendship.status == "pending").all()

    result = []
    for f in friendships:
        requester = db.query(User).filter(User.id == f.requester_id).first()
        result.append({"id": str(f.id), "status": f.status, "other_user_name": requester.name, "other_user_email": requester.email})
    return result

@router.delete("/{friendship_id}")
def remove_friend(friendship_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        or_(Friendship.requester_id == user.id, Friendship.addressee_id == user.id)
    ).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")
    db.delete(friendship)
    db.commit()
    return {"message": "Removed"}
