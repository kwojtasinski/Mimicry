# Configuration

Mimicry uses YAML files to define how data should be generated (table configuration) and where it should be sent (sink configuration).

## Table Configuration

A table configuration file defines the schema of the data to be generated. It specifies the table's name, description, locale for data generation, and a list of fields.

**Example `my_table_schema.yaml`:**

```yaml
name: DimEmployees
locale: en
description: Dimension table for employee information.
fields:
- description: Unique identifier for the employee.
  mimesis_field_args: []
  mimesis_field_name: person.identifier # Placeholder, adjust with actual mimesis field
  name: employee_id
- description: National identification number for the employee.
  mimesis_field_args: []
  mimesis_field_name: person.identifier # Placeholder, adjust with actual mimesis field
  name: national_id
- description: Full name of the employee.
  mimesis_field_args: []
  mimesis_field_name: person.full_name
  name: full_name
- description: Job title or position held by the employee.
  mimesis_field_args: []
  mimesis_field_name: person.occupation
  name: job_title
- description: Work email address of the employee.
  mimesis_field_args: []
  mimesis_field_name: person.email
  name: email
- description: Date when the employee was hired.
  mimesis_field_args: []
  mimesis_field_name: datetime.date
  name: hire_date
- description: Annual salary of the employee in USD.
  mimesis_field_args: []
  mimesis_field_name: finance.price # Placeholder, adjust with actual mimesis field
  name: salary
- description: Employee ID of the manager (foreign key).
  mimesis_field_args: []
  mimesis_field_name: person.identifier # Placeholder, adjust with actual mimesis field
  name: manager_id_fk
- description: City where the employee's office is located.
  mimesis_field_args: []
  mimesis_field_name: address.city
  name: office_location
- description: Indicates if the employee is currently active.
  mimesis_field_args: []
  mimesis_field_name: development.boolean
  name: is_active
```

Please refer to the [Mimesis documentation](https://mimesis.name) for a complete list of available fields and their parameters.

**Fields in `TableConfiguration`:**

*   `name` (str): The name of the table.
*   `description` (str): A description of the table.
*   `locale` (str, optional): The Mimesis locale to use for data generation (e.g., "en", "de", "ja"). Defaults to "en".
*   `fields` (list): A list of `FieldConfiguration` objects.

**Fields in `FieldConfiguration`:**

*   `name` (str): The name of the field (column name).
*   `description` (str): A description of the field.
*   `mimesis_field_name` (str): The Mimesis provider and method to use (e.g., "person.full_name", "address.city", "numeric.float_number").
*   `mimesis_field_args` (list, optional): A list of positional arguments to pass to the Mimesis method.
*   `mimesis_field_kwargs` (dict, optional): A dictionary of keyword arguments to pass to the Mimesis method.

## Sink Configuration

A sink configuration file defines where the generated data should be stored or sent.

**Example `my_sink_config.yaml`:**

```yaml
configuration:
  type_of_sink: "delta_lake"  # or "duckdb", "postgres", "kafka", "iceberg"
  # Sink-specific configuration below
  path: "/path/to/delta_lake_table" # Example for delta_lake
  table_name: "users_table" # Example for duckdb, postgres, iceberg
  # producer_config: {} # Example for kafka
  # topic: "my_topic" # Example for kafka
  # catalog_properties: {} # Example for iceberg
```

The top-level key is `configuration`, which then contains the specific sink type and its parameters. Refer to the [Sinks](./sinks.md) documentation for details on each sink type.
