from peewee import Model, DateTimeField, AutoField, CharField, BooleanField
from datetime import datetime


class BaseModel(Model):
    """
    Base model class for all domain models.
    Provides common fields and functionality across all models.
    """
    id = AutoField(primary_key=True)
    created_at = DateTimeField(default=datetime.utcnow, null=True)
    updated_at = DateTimeField(default=datetime.utcnow, null=True)

    class Meta:
        """Meta configuration for BaseModel."""
        abstract = True

    def save(self, *args, **kwargs):
        """
        Override save to update the updated_at timestamp.
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

    # Dynamically generate builder chaining methods based on the model's fields
    def __getattr__(self, attr):
        """
        Intercepts access to non-existing methods and dynamically creates 'set_<field_name>' methods
        for all fields present in the model.
        
        This enables fluent setter syntax like:
            user = User()
            user.set_username("alice").set_email("alice@test.com")
        """
        if attr.startswith('set_'):
            field_name = attr[4:]  # Remove 'set_' prefix to get the field name
            # Check if the field exists in the model by trying to get the field object
            try:
                # Try to get the field from metaclass
                if hasattr(self._meta, 'fields') and field_name in self._meta.fields:
                    def setter(value):
                        setattr(self, field_name, value)
                        return self  # Return self for chaining
                    return setter
                # Also check if it's a valid attribute that can be set
                elif hasattr(self.__class__, field_name):
                    def setter(value):
                        setattr(self, field_name, value)
                        return self  # Return self for chaining
                    return setter
            except (AttributeError, KeyError):
                pass
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr}'")

    @classmethod
    def apply_dynamic_methods(cls):
        """
        Apply dynamic builder methods for setting model fields automatically.
        """
        for field in cls._meta.fields:
            # Create and attach a setter method dynamically for each field
            method_name = f"set_{field}"
            setter_method = cls.create_setter_method(field)
            setattr(cls, method_name, setter_method)

    @staticmethod
    def create_setter_method(field):
        """
        Creates a setter method for a field that allows for chaining.
        """
        def setter(self, value):
            setattr(self, field, value)
            return self  # Return self for method chaining
        return setter

