"""Data models for schema validation and type safety."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Union
import json
import yaml


@dataclass(frozen=True)
class DataSource:
    """Represents a data source with provenance information."""
    provider: str
    dataset: str
    field: Optional[str] = None
    url: Optional[str] = None
    version: Optional[str] = None
    year: Optional[int] = None
    note: Optional[str] = None


@dataclass(frozen=True)
class FieldConstraints:
    """Validation constraints for a data field."""
    unique: Optional[bool] = None
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None


@dataclass(frozen=True)
class FieldDefinition:
    """Complete definition of a data field."""
    name: str
    source_name: str
    data_type: str
    nullable: bool
    description: str
    source: DataSource
    constraints: Optional[FieldConstraints] = None
    values: Optional[Dict[str, str]] = None  # For categorical fields
    transformations: Optional[List[str]] = None
    primary_key: bool = False
    foreign_key: Optional[str] = None


@dataclass(frozen=True)
class DatasetDefinition:
    """Complete definition of a dataset."""
    name: str
    description: str
    source: str
    fields: Dict[str, FieldDefinition]


@dataclass(frozen=True)
class TransformationRule:
    """Describes a data transformation."""
    name: str
    description: str
    input_fields: List[str]
    output_field: str
    logic: str
    mapping: Optional[Dict[str, str]] = None


class DataDictionary:
    """Manages the complete data dictionary."""
    
    def __init__(self, schema_path: Path):
        """
        Initialize the data dictionary from a schema file.
        
        Args:
            schema_path: Path to the schema.json file
        """
        self.schema_path = schema_path
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the schema from the JSON file."""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        self.version = self.schema.get('version', '1.0.0')
        self.title = self.schema.get('title', 'Data Dictionary')
        self.description = self.schema.get('description', '')
        
        # Parse datasets
        self.datasets: Dict[str, DatasetDefinition] = {}
        for dataset_name, dataset_info in self.schema.get('datasets', {}).items():
            fields = {}
            for field_name, field_info in dataset_info.get('fields', {}).items():
                # Parse source
                source_info = field_info.get('source', {})
                source = DataSource(
                    provider=source_info.get('provider', ''),
                    dataset=source_info.get('dataset', ''),
                    field=source_info.get('field'),
                    url=source_info.get('url'),
                    version=source_info.get('version'),
                    year=source_info.get('year'),
                    note=source_info.get('note')
                )
                
                # Parse constraints
                constraints_info = field_info.get('constraints', {})
                constraints = FieldConstraints(
                    unique=constraints_info.get('unique'),
                    min=constraints_info.get('min'),
                    max=constraints_info.get('max'),
                    min_length=constraints_info.get('minLength'),
                    max_length=constraints_info.get('maxLength'),
                    pattern=constraints_info.get('pattern')
                ) if constraints_info else None
                
                # Create field definition
                field_def = FieldDefinition(
                    name=field_name,
                    source_name=field_info.get('source_name', field_name),
                    data_type=field_info.get('data_type', 'string'),
                    nullable=field_info.get('nullable', True),
                    description=field_info.get('description', ''),
                    source=source,
                    constraints=constraints,
                    values=field_info.get('values'),
                    transformations=field_info.get('transformations'),
                    primary_key=field_info.get('primary_key', False),
                    foreign_key=field_info.get('foreign_key')
                )
                fields[field_name] = field_def
            
            dataset_def = DatasetDefinition(
                name=dataset_name,
                description=dataset_info.get('description', ''),
                source=dataset_info.get('source', ''),
                fields=fields
            )
            self.datasets[dataset_name] = dataset_def
        
        # Parse transformations
        self.transformations: Dict[str, TransformationRule] = {}
        for transform_name, transform_info in self.schema.get('transformations', {}).items():
            input_fields = transform_info.get('input', [])
            if isinstance(input_fields, str):
                input_fields = [input_fields]
            
            transform_rule = TransformationRule(
                name=transform_name,
                description=transform_info.get('description', ''),
                input_fields=input_fields,
                output_field=transform_info.get('output', ''),
                logic=transform_info.get('logic', ''),
                mapping=transform_info.get('mapping')
            )
            self.transformations[transform_name] = transform_rule
    
    def get_dataset(self, name: str) -> Optional[DatasetDefinition]:
        """Get a dataset definition by name."""
        return self.datasets.get(name)
    
    def get_field(self, dataset_name: str, field_name: str) -> Optional[FieldDefinition]:
        """Get a field definition from a specific dataset."""
        dataset = self.get_dataset(dataset_name)
        if dataset:
            return dataset.fields.get(field_name)
        return None
    
    def get_primary_keys(self, dataset_name: str) -> List[str]:
        """Get primary key field names for a dataset."""
        dataset = self.get_dataset(dataset_name)
        if dataset:
            return [name for name, field in dataset.fields.items() if field.primary_key]
        return []
    
    def get_foreign_keys(self, dataset_name: str) -> Dict[str, str]:
        """Get foreign key relationships for a dataset."""
        dataset = self.get_dataset(dataset_name)
        if dataset:
            return {
                name: field.foreign_key 
                for name, field in dataset.fields.items() 
                if field.foreign_key
            }
        return {}
    
    def validate_field_value(
        self, 
        dataset_name: str, 
        field_name: str, 
        value: any
    ) -> List[str]:
        """
        Validate a field value against its constraints.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        field = self.get_field(dataset_name, field_name)
        if not field:
            return [f"Unknown field: {dataset_name}.{field_name}"]
        
        errors = []
        
        # Check null values
        if value is None or value == '':
            if not field.nullable:
                errors.append(f"Field {field_name} cannot be null")
            return errors  # Don't validate constraints for null values
        
        # Type validation
        if field.data_type == 'integer':
            try:
                int_value = int(value)
                value = int_value
            except (ValueError, TypeError):
                errors.append(f"Field {field_name} must be an integer")
                return errors
        elif field.data_type == 'float':
            try:
                float_value = float(value)
                value = float_value
            except (ValueError, TypeError):
                errors.append(f"Field {field_name} must be a number")
                return errors
        
        # Constraint validation
        if field.constraints:
            if field.constraints.min is not None and value < field.constraints.min:
                errors.append(f"Field {field_name} must be >= {field.constraints.min}")
            
            if field.constraints.max is not None and value > field.constraints.max:
                errors.append(f"Field {field_name} must be <= {field.constraints.max}")
            
            if field.constraints.min_length is not None:
                if len(str(value)) < field.constraints.min_length:
                    errors.append(f"Field {field_name} must be at least {field.constraints.min_length} characters")
            
            if field.constraints.max_length is not None:
                if len(str(value)) > field.constraints.max_length:
                    errors.append(f"Field {field_name} must be at most {field.constraints.max_length} characters")
            
            if field.constraints.pattern is not None:
                import re
                if not re.match(field.constraints.pattern, str(value)):
                    errors.append(f"Field {field_name} must match pattern: {field.constraints.pattern}")
        
        # Categorical value validation
        if field.values and str(value) not in field.values:
            valid_values = list(field.values.keys())
            errors.append(f"Field {field_name} must be one of: {valid_values}")
        
        return errors
    
    def get_transformation(self, name: str) -> Optional[TransformationRule]:
        """Get a transformation rule by name."""
        return self.transformations.get(name)
    
    def list_datasets(self) -> List[str]:
        """Get names of all datasets."""
        return list(self.datasets.keys())
    
    def list_transformations(self) -> List[str]:
        """Get names of all transformations."""
        return list(self.transformations.keys())


class SourceRegistry:
    """Manages data source metadata and provenance."""
    
    def __init__(self, sources_path: Path):
        """
        Initialize the source registry.
        
        Args:
            sources_path: Path to the sources.yaml file
        """
        self.sources_path = sources_path
        self._load_sources()
    
    def _load_sources(self) -> None:
        """Load source metadata from YAML file."""
        with open(self.sources_path, 'r', encoding='utf-8') as f:
            self.sources_data = yaml.safe_load(f)
    
    def get_source_info(self, provider: str) -> Optional[Dict]:
        """Get information about a data provider."""
        return self.sources_data.get('sources', {}).get(provider)
    
    def get_current_data_info(self, snapshot_name: str) -> Optional[Dict]:
        """Get information about a current data snapshot."""
        return self.sources_data.get('current_data', {}).get(snapshot_name)
    
    def list_providers(self) -> List[str]:
        """Get names of all data providers."""
        return list(self.sources_data.get('sources', {}).keys())
    
    def list_snapshots(self) -> List[str]:
        """Get names of all current data snapshots."""
        return list(self.sources_data.get('current_data', {}).keys())