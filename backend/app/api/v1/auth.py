import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.models.watchlist import Watchlist, WatchlistItem
from app.schemas.auth import Token, UserLogin, UserOut, UserRegister
from app.api.deps import get_current_active_user

router = APIRouter()


async def seed_guest_watchlist(db: AsyncSession, user_id: str) -> Watchlist:
    """Create default initial watchlist with Indian market stocks for new/guest users."""
    watchlist = Watchlist(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Main Watchlist",
        description="High-conviction core portfolio & market leaders",
        is_default=True,
    )
    db.add(watchlist)
    await db.flush()

    default_symbols = ["INFY", "TCS", "HDFCBANK", "TATAMOTORS", "RELIANCE"]
    for sym in default_symbols:
        item = WatchlistItem(
            id=str(uuid.uuid4()),
            watchlist_id=watchlist.id,
            symbol=sym,
            custom_tag="Core",
        )
        db.add(item)
    return watchlist


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    existing = await db.execute(select(User).where(User.email == user_in.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    user = User(
        id=str(uuid.uuid4()),
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_guest=False,
    )
    db.add(user)
    await db.flush()

    # Seed default watchlist
    await seed_guest_watchlist(db, user.id)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 compatible token login."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/guest", response_model=Token)
async def guest_login(
    db: AsyncSession = Depends(get_db),
):
    """
    1-Click instant guest login for hackathon judges and frictionless demo access.
    Creates a dedicated pre-configured guest session.
    """
    guest_id = str(uuid.uuid4())
    guest_email = f"judge_{guest_id[:8]}@marketpulse.demo"

    user = User(
        id=guest_id,
        email=guest_email,
        hashed_password=get_password_hash("demo_guest_secret"),
        full_name="Hackathon Evaluator",
        is_active=True,
        is_guest=True,
    )
    db.add(user)
    await db.flush()

    await seed_guest_watchlist(db, user.id)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """Get current authenticated user profile."""
    return UserOut.model_validate(current_user)
