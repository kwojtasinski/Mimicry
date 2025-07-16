# Interactive Table Definition

The `mimicry define` command provides an interactive CLI workflow for creating table definitions using the `questionary` library. This feature allows users to dynamically configure table schemas based on available mimesis providers and methods.

## Usage

```bash
# Interactive table definition
mimicry define

# Save to specific file
mimicry define -o my_table.yaml
```

## Interactive Workflow

The command guides you through the following steps:

### 1. Basic Table Information
- **Table Name**: Enter a name for your table
- **Description**: Provide a description of what the table represents
- **Locale**: Select the locale for data generation (en, de, es, fr, it, pt, ru)

### 2. Field Configuration
For each field, you'll be prompted to:
- **Select Provider**: Choose from available mimesis providers (Person, Address, DateTime, etc.)
- **Select Method**: Choose a specific method from the selected provider
- **Field Name**: Enter a name for the field
- **Field Description**: Provide a description of the field
- **Configure Arguments**: Optionally provide arguments and keyword arguments for the method

### 3. Output Generation
The tool generates a YAML configuration file that matches the existing `TableConfiguration` format.

## Example Session

```
$ mimicry define

=== Interactive Table Definition ===

? Enter table name: user_profiles
? Enter table description: User profile information
? Select locale: en

Adding field #1
? Select a mimesis provider: Person
? Select a method from Person: username
? Enter field name: username
? Enter field description: Unique username
? Do you want to provide arguments for this method? No
? Do you want to add another field? Yes

Adding field #2
? Select a mimesis provider: DateTime
? Select a method from DateTime: date
? Enter field name: birth_date
? Enter field description: Date of birth
Method signature: date(start=1900, end=2100)
? Do you want to provide arguments for this method? Yes
? Add a keyword argument? Yes
? Enter argument name: start
? Select argument type: integer
? Enter integer value for start: 1950
? Add a keyword argument? Yes
? Enter argument name: end
? Select argument type: integer
? Enter integer value for end: 2005
? Add a keyword argument? No
? Do you want to add another field? No

✅ Table configuration saved to: user_profiles.yaml
📊 Table 'user_profiles' with 2 fields
```

## Generated YAML

The interactive tool generates standard YAML configuration files:

```yaml
name: user_profiles
description: User profile information
locale: en
fields:
- name: username
  description: Unique username
  mimesis_field_name: person.username
  mimesis_field_args: []
  mimesis_field_kwargs: {}
- name: birth_date
  description: Date of birth
  mimesis_field_name: datetime.date
  mimesis_field_args: []
  mimesis_field_kwargs:
    start: 1950
    end: 2005
```

## Benefits

- **User-friendly**: No need to manually write YAML configurations
- **Discovery**: Explore available mimesis providers and methods interactively
- **Validation**: Built-in validation for field names and arguments
- **Flexibility**: Support for method arguments and keyword arguments
- **Error Prevention**: Reduces manual errors in configuration creation

## Advanced Features

### Method Arguments
The tool supports both positional arguments and keyword arguments for mimesis methods:
- **Positional args**: Stored in `mimesis_field_args` list
- **Keyword args**: Stored in `mimesis_field_kwargs` dictionary

### Argument Types
Supported argument types:
- **string**: Text values
- **integer**: Numeric values
- **float**: Decimal values
- **boolean**: True/False values

### Method Signatures
The tool shows method signatures when available to help users understand what arguments are expected.

## Integration

The generated YAML files are fully compatible with existing Mimicry commands:

```bash
# Generate data using the created configuration
mimicry generate -s sink_config.yaml -p user_profiles.yaml -i 5 -c 100 -b 1

# Serve as an API
mimicry serve -s user_profiles.yaml
```