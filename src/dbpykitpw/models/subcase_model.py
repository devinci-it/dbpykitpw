"""
SubCase Model - Domain model for SubCase entities.
"""

from peewee import AutoField, CharField, DateTimeField
from datetime import datetime

from .base_model import BaseModel


class SubCase(BaseModel):
    """
    SubCase model representing a customer service case.

    Attributes:
        id: Unique identifier
        customer_company: Name of the customer company
        user_status: Status of the user/case
        address: Address associated with the case
        scheduled_datetime: When the case is scheduled
        arrive_datetime: When service arrived
        deleted_at: Soft delete timestamp (null if not deleted)
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    id = AutoField(primary_key=True)
    customer_company = CharField(max_length=255)
    user_status = CharField(max_length=100)
    address = CharField(max_length=255)
    scheduled_datetime = DateTimeField(default=datetime.utcnow)
    arrive_datetime = DateTimeField(default=datetime.utcnow, null=True)
    deleted_at = DateTimeField(null=True)

    class Meta:
        """Meta configuration for SubCase."""

        table_name = "subcase"

    def __repr__(self) -> str:
        """Detailed string representation of SubCase."""
        return (
            f"SubCase(id={self.id}, customer_company='{self.customer_company}', "
            f"user_status='{self.user_status}', address='{self.address}', "
            f"deleted_at={self.deleted_at})"
        )

    def __str__(self) -> str:
        """User-friendly string representation of SubCase."""
        status = "DELETED" if self.deleted_at else "ACTIVE"
        return f"SubCase #{self.id} - {self.customer_company} ({status})"

    def is_deleted(self) -> bool:
        """Check if this record is soft deleted."""
        return self.deleted_at is not None

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "customer_company": self.customer_company,
            "user_status": self.user_status,
            "address": self.address,
            "scheduled_datetime": self.scheduled_datetime.isoformat() if self.scheduled_datetime else None,
            "arrive_datetime": self.arrive_datetime.isoformat() if self.arrive_datetime else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
