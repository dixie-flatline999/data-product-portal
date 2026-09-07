import uuid

from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy

from app.database.database import Base
from app.shared.model import BaseORM

from typing import TYPE_CHECKING

# Added for type checking in the IDE, disabled at runtime to avoid circular dependencies
if TYPE_CHECKING:
    from app.groups.model import GroupMembership
    from app.authorization.role_assignments.data_product.model import (
        DataProductRoleAssignment,
    )
    from app.authorization.role_assignments.global_.model import (
        GlobalRoleAssignment,
    )
    from app.data_products.model import DataProduct


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

    data_product_roles: Mapped[list["DataProductRoleAssignment"]] = relationship(
        foreign_keys="DataProductRoleAssignment.identity_id",
        back_populates="identity",
        # Deliberately lazy:
        #  - Used in limited cases, only on a single identity
        #  - Complicates get_authenticated_user
        #  - Private dataset test cases become more complex
        #    (need to manipulate the session to avoid an identity being cached with a
        #     membership field with raise load strategy)
        lazy="select",
    )
    data_products: Mapped[list["DataProduct"]] = association_proxy(
        "data_product_roles",
        "data_product",
    )

    global_role: Mapped["GlobalRoleAssignment | None"] = relationship(
        foreign_keys="GlobalRoleAssignment.identity_id",
        back_populates="identity",
        lazy="select",
    )