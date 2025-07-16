"""Interactive table definition functionality using questionary."""

import inspect
import logging
from typing import Any, Dict, List, Optional, Tuple

import questionary
import yaml
from mimesis import Locale
from mimesis.providers import BaseProvider

from mimicry.models import FieldConfiguration, TableConfiguration

logger = logging.getLogger(__name__)


def _is_valid_float(value: str) -> bool:
    """Check if a string represents a valid float.
    
    Args:
        value: The string to check.
        
    Returns:
        bool: True if valid float, False otherwise.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_mimesis_providers() -> Dict[str, type]:
    """Get all available mimesis providers.
    
    Returns:
        Dict[str, type]: Dictionary mapping provider names to provider classes.
    """
    import mimesis.providers as providers
    
    provider_classes = {}
    for name in dir(providers):
        obj = getattr(providers, name)
        if (
            inspect.isclass(obj) 
            and issubclass(obj, BaseProvider) 
            and obj is not BaseProvider
        ):
            provider_classes[name] = obj
    
    return provider_classes


def get_provider_methods(provider_class: type) -> List[str]:
    """Get all available methods for a provider class.
    
    Args:
        provider_class: The provider class to inspect.
        
    Returns:
        List[str]: List of method names.
    """
    methods = []
    for name in dir(provider_class):
        if not name.startswith('_'):
            attr = getattr(provider_class, name)
            if callable(attr) and not name in ['reseed', 'seed']:
                methods.append(name)
    
    return sorted(methods)


def get_method_signature(provider_class: type, method_name: str) -> Optional[inspect.Signature]:
    """Get the signature of a provider method.
    
    Args:
        provider_class: The provider class.
        method_name: The method name.
        
    Returns:
        Optional[inspect.Signature]: The method signature, or None if not found.
    """
    try:
        method = getattr(provider_class, method_name)
        if callable(method):
            return inspect.signature(method)
        return None
    except (AttributeError, ValueError, TypeError):
        return None


def prompt_for_basic_table_info() -> Tuple[str, str, str]:
    """Prompt user for basic table information.
    
    Returns:
        Tuple[str, str, str]: Table name, description, and locale.
        
    Raises:
        KeyboardInterrupt: If user cancels the operation.
    """
    table_name = questionary.text(
        "Enter table name:",
        validate=lambda x: len(x.strip()) > 0 or "Table name cannot be empty"
    ).ask()
    
    if table_name is None:
        raise KeyboardInterrupt("Operation cancelled by user")
    
    description = questionary.text(
        "Enter table description:",
        validate=lambda x: len(x.strip()) > 0 or "Description cannot be empty"
    ).ask()
    
    if description is None:
        raise KeyboardInterrupt("Operation cancelled by user")
    
    locale = questionary.select(
        "Select locale:",
        choices=["en", "de", "es", "fr", "it", "pt", "ru"],
        default="en"
    ).ask()
    
    if locale is None:
        raise KeyboardInterrupt("Operation cancelled by user")
    
    return table_name, description, locale


def prompt_for_provider_selection(providers: Dict[str, type]) -> type:
    """Prompt user to select a mimesis provider.
    
    Args:
        providers: Dictionary of available providers.
        
    Returns:
        type: The selected provider class.
        
    Raises:
        KeyboardInterrupt: If user cancels the operation.
    """
    provider_choices = sorted(providers.keys())
    
    selected_provider = questionary.select(
        "Select a mimesis provider:",
        choices=provider_choices
    ).ask()
    
    if selected_provider is None:
        raise KeyboardInterrupt("Operation cancelled by user")
    
    return providers[selected_provider]


def prompt_for_method_selection(provider_class: type, provider_name: str) -> str:
    """Prompt user to select a method from a provider.
    
    Args:
        provider_class: The provider class.
        provider_name: The provider name for display.
        
    Returns:
        str: The selected method name.
        
    Raises:
        KeyboardInterrupt: If user cancels the operation.
    """
    methods = get_provider_methods(provider_class)
    
    selected_method = questionary.select(
        f"Select a method from {provider_name}:",
        choices=methods
    ).ask()
    
    if selected_method is None:
        raise KeyboardInterrupt("Operation cancelled by user")
    
    return selected_method


def prompt_for_field_configuration(provider_name: str, method_name: str, provider_class: type) -> FieldConfiguration:
    """Prompt user to configure a field.
    
    Args:
        provider_name: The provider name.
        method_name: The method name.
        provider_class: The provider class.
        
    Returns:
        FieldConfiguration: The configured field.
    """
    field_name = questionary.text(
        "Enter field name:",
        validate=lambda x: len(x.strip()) > 0 or "Field name cannot be empty"
    ).ask()
    
    field_description = questionary.text(
        "Enter field description:",
        validate=lambda x: len(x.strip()) > 0 or "Field description cannot be empty"
    ).ask()
    
    mimesis_field_name = f"{provider_name.lower()}.{method_name}"
    
    # Get method signature to help with arguments
    signature = get_method_signature(provider_class, method_name)
    mimesis_field_args = []
    mimesis_field_kwargs = {}
    
    if signature:
        # Show method signature to user
        questionary.print(f"Method signature: {signature}")
        
        # Ask if user wants to provide arguments
        if questionary.confirm("Do you want to provide arguments for this method?").ask():
            # For simplicity, we'll ask for kwargs as key-value pairs
            while True:
                add_kwarg = questionary.confirm("Add a keyword argument?").ask()
                if not add_kwarg:
                    break
                    
                key = questionary.text("Enter argument name:").ask()
                value_type = questionary.select(
                    "Select argument type:",
                    choices=["string", "integer", "float", "boolean"]
                ).ask()
                
                if value_type == "string":
                    value = questionary.text(f"Enter value for {key}:").ask()
                elif value_type == "integer":
                    value_str = questionary.text(
                        f"Enter integer value for {key}:",
                        validate=lambda x: x.lstrip('-').isdigit() or "Must be a valid integer"
                    ).ask()
                    value = int(value_str)
                elif value_type == "float":
                    value_str = questionary.text(
                        f"Enter float value for {key}:",
                        validate=lambda x: _is_valid_float(x) or "Must be a valid float"
                    ).ask()
                    value = float(value_str)
                elif value_type == "boolean":
                    value = questionary.confirm(f"Enter boolean value for {key}:").ask()
                
                mimesis_field_kwargs[key] = value
    
    return FieldConfiguration(
        name=field_name,
        description=field_description,
        mimesis_field_name=mimesis_field_name,
        mimesis_field_args=mimesis_field_args,
        mimesis_field_kwargs=mimesis_field_kwargs
    )


def interactive_table_definition() -> TableConfiguration:
    """Main interactive function to define a table configuration.
    
    Returns:
        TableConfiguration: The complete table configuration.
    """
    questionary.print("=== Interactive Table Definition ===")
    
    # Get basic table info
    table_name, description, locale = prompt_for_basic_table_info()
    
    # Get available providers
    providers = get_mimesis_providers()
    
    fields = []
    
    # Add fields interactively
    while True:
        questionary.print(f"\nAdding field #{len(fields) + 1}")
        
        # Select provider
        provider_class = prompt_for_provider_selection(providers)
        provider_name = provider_class.__name__
        
        # Select method
        method_name = prompt_for_method_selection(provider_class, provider_name)
        
        # Configure field
        field_config = prompt_for_field_configuration(provider_name, method_name, provider_class)
        fields.append(field_config)
        
        # Ask if user wants to add more fields
        if not questionary.confirm("Do you want to add another field?").ask():
            break
    
    return TableConfiguration(
        name=table_name,
        description=description,
        locale=locale,
        fields=fields
    )


def save_table_configuration(table_config: TableConfiguration, output_path: Optional[str] = None) -> str:
    """Save table configuration to a YAML file.
    
    Args:
        table_config: The table configuration to save.
        output_path: Optional output path. If None, uses table name.
        
    Returns:
        str: The path where the configuration was saved.
    """
    if output_path is None:
        output_path = f"{table_config.name}.yaml"
    
    # Convert to dict for YAML serialization
    config_dict = table_config.model_dump()
    
    with open(output_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
    
    return output_path