from typing import Optional
from datetime import datetime

from sqlalchemy import Integer, String, TIMESTAMP, text
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=True,
    )

