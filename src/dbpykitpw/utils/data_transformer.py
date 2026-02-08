"""
Data Transformer - Utility for converting between different data formats.
"""

from typing import Type, Optional, Dict, Any
import json
from peewee import Model


class DataTransformer:
    """
    Utility class for transforming data between models, dictionaries, and JSON.
    Provides seamless conversion between different data representations.
    """

    @staticmethod
    def model_to_dict(model: Model) -> Dict[str, Any]:
        """
        Convert a Peewee model instance to a dictionary.

        Args:
            model: Peewee model instance

        Returns:
            Dictionary representation of the model
        """
        return model.__data__

    @staticmethod
    def model_to_json(model: Model) -> str:
        """
        Convert a Peewee model instance to a JSON string.

        Args:
            model: Peewee model instance

        Returns:
            JSON string representation of the model
        """
        return json.dumps(model.__data__, default=str)

    @staticmethod
    def row_to_domain(row: Optional[Model], domain_class: Type[Model]) -> Optional[Model]:
        """
        Convert a raw Peewee row (model instance) to a domain model object.

        Args:
            row: Raw Peewee model instance or None
            domain_class: Target domain model class

        Returns:
            Domain model instance or None if row is None
        """
        if not row:
            return None

        # Use the field data from the row to construct a domain model object
        return domain_class(**row.__data__)

    @staticmethod
    def domain_to_dict(domain_object: Model) -> Dict[str, Any]:
        """
        Convert a domain model object to a dictionary for database operations.

        Args:
            domain_object: Model instance

        Returns:
            Dictionary representation for database use
        """
        result = {}
        # Get all field values from the model
        for key, value in domain_object.__data__.items():
            result[key] = value
        return result

    @staticmethod
    def domain_to_json(domain_object: Model) -> str:
        """
        Convert a domain model object to a JSON string.

        Args:
            domain_object: Model instance

        Returns:
            JSON string representation
        """
        return json.dumps(domain_object.__data__, default=str)

    @staticmethod
    def dict_to_model(data: Dict[str, Any], model_class: Type[Model]) -> Model:
        """
        Convert a dictionary to a model instance.

        Args:
            data: Dictionary of field values
            model_class: Target model class

        Returns:
            Model instance
        """
        return model_class(**data)

    @staticmethod
    def json_to_model(json_str: str, model_class: Type[Model]) -> Model:
        """
        Convert a JSON string to a model instance.

        Args:
            json_str: JSON string representation
            model_class: Target model class

        Returns:
            Model instance
        """
        data = json.loads(json_str)
        return model_class(**data)

    @staticmethod
    def json_to_dict(json_str: str) -> Dict[str, Any]:
        """
        Convert a JSON string to a dictionary.

        Args:
            json_str: JSON string

        Returns:
            Dictionary representation
        """
        return json.loads(json_str)

    @staticmethod
    def dict_to_json(data: Dict[str, Any]) -> str:
        """
        Convert a dictionary to a JSON string.

        Args:
            data: Dictionary to convert

        Returns:
            JSON string
        """
        return json.dumps(data, default=str)

    def __repr__(self) -> str:
        """String representation."""
        return "DataTransformer()"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return "Data Transformer Utility"
