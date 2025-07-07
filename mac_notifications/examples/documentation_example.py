"""Example module demonstrating comprehensive documentation standards.

This module shows best practices for documenting Python code in the
Mac Notifications project. It includes examples of module, class, and
function documentation with proper type hints and detailed descriptions.

The documentation follows Google style guide and includes:
- Comprehensive docstrings
- Type hints for all parameters and returns
- Usage examples
- Performance notes
- Cross-references

Usage:
    from examples.documentation_example import ExampleClass
    
    instance = ExampleClass("example")
    result = instance.process_data({"key": "value"})
    
See Also:
    - Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
    - Type Hints PEP 484: https://www.python.org/dev/peps/pep-0484/
"""

from typing import Dict, List, Optional, Union, Tuple, Any
from datetime import datetime
import logging

# Module-level logger
logger = logging.getLogger(__name__)


class ExampleClass:
    """Example class showing proper documentation.
    
    This class demonstrates how to document a Python class properly,
    including attributes, methods, and usage examples.
    
    Attributes:
        name (str): The name identifier for this instance
        config (Dict[str, Any]): Configuration dictionary
        _internal (bool): Private attribute (not in public API)
        
    Example:
        >>> instance = ExampleClass("test")
        >>> instance.process_data({"type": "example"})
        (True, None, {'processed': 1})
        
    Note:
        This class is thread-safe for read operations only.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize ExampleClass with name and optional config.
        
        Args:
            name: Identifier for this instance. Must be non-empty
                and contain only alphanumeric characters.
            config: Optional configuration dict. Supported keys:
                - timeout (int): Processing timeout in seconds
                - retries (int): Number of retry attempts
                - verbose (bool): Enable detailed logging
                
        Raises:
            ValueError: If name is empty or contains invalid characters
            TypeError: If config is not a dictionary
            
        Example:
            >>> instance = ExampleClass("processor", {"timeout": 30})
        """
        if not name or not name.isalnum():
            raise ValueError(f"Invalid name: {name}")
            
        self.name = name
        self.config = config or {}
        self._internal = True
        
        logger.info(f"Initialized {self.__class__.__name__} '{name}'")
    
    def process_data(
        self,
        data: Dict[str, Any],
        validate: bool = True
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Process input data and return results.
        
        Processes the provided data dictionary according to its type
        and the instance configuration. Supports validation and
        returns detailed results.
        
        Args:
            data: Input data dictionary. Required keys:
                - type (str): Type of data to process
                - content (Any): The actual data
            validate: Whether to validate input data before processing.
                Default is True for safety.
                
        Returns:
            Tuple containing:
                - success (bool): Whether processing succeeded
                - error (Optional[str]): Error message if failed
                - metadata (Dict[str, Any]): Processing metadata
                
        Raises:
            KeyError: If required keys are missing from data
            ValueError: If data validation fails
            
        Example:
            >>> result = instance.process_data({
            ...     "type": "notification",
            ...     "content": {"message": "Hello"}
            ... })
            >>> success, error, meta = result
            >>> print(f"Success: {success}, Items: {meta['processed']}")
            Success: True, Items: 1
            
        Performance:
            Average processing time: 10-50ms depending on data size
            Memory usage: O(n) where n is size of content
        """
        # Implementation here
        return (True, None, {"processed": 1})
