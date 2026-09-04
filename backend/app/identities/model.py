import uuid

from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

from typing import TYPE_CHECKING

# Added for type checking in the IDE, disabled at runtime to avoid circular dependencies
if TYPE_CHECKING:
    from app.groups.model import GroupMembership


class Identity(Base, BaseORM):
    __tablename__ = "identities"
    __table_args__ = (
        CheckConstraint(
            "type IN ('user', 'group', 'machine_user')",
            name="ck_identities_type",
        ),
        UniqueConstraint(
            "type",
            "external_id",
            name="uq_identities_type_external_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    type: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[str] = mapped_column(String, nullable=False)

    # Must be below the "type" column definition
    __mapper_args__ = {
        "polymorphic_on": type
    }

    member_of: Mapped[list["GroupMembership"]] = relationship(
        back_populates="member",
        foreign_keys="GroupMembership.member_identity_id",
        cascade="all, delete-orphan",
        lazy="raise",
    )