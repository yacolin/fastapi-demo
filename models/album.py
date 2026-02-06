from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, String, TIMESTAMP, text
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


Base = declarative_base()


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    liked: Mapped[int] = mapped_column(BigInteger, server_default=text("0"), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False,
    )

