"""
Base Model - Base class for all Peewee models.
"""

from re import A
from peewee import Model, DateTimeField, AutoField
from datetime import datetime
from typing import Optional


class BaseModel(Model):
    """
    Base model class for all domain models.
    Provides common fields and functionality across all models.
    """
    id=AutoField(primary_key=True)
    created_at = DateTimeField(default=datetime.utcnow, null=True)
    updated_at = DateTimeField(default=datetime.utcnow, null=True)

    class Meta:
        """Meta configuration for BaseModel."""

        abstract = True

    def save(self, *args, **kwargs):
        """
        Override save to update the updated_at timestamp.

        Returns:
            The model instance
        """
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __repr__(self) -> str:
        """String representation of the model."""
        model_name = self.__class__.__name__
        if hasattr(self, "id"):
            return f"{model_name}(id={self.id})"
        return f"{model_name}()"

    def __str__(self) -> str:
        """User-friendly string representation."""
        model_name = self.__class__.__name__
        if hasattr(self, "id"):
            return f"{model_name} #{self.id}"
        return model_name
