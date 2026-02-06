from typing import Optional
from datetime import datetime

from sqlalchemy import Integer, String, TIMESTAMP, text
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


Base = declarative_base()


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    champions: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    divide: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    part: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=True,
    )

