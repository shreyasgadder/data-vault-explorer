# DataVault Explorer

DataVault Explorer is a robust tool for validating database entities and exporting query results across multiple database systems like Hive, Impala, PostgreSQL, Snowflake, Oracle, and MySQL.

---

## Index

- [Project Overview](#project-overview)
- [Folder Structure](#folder-structure)
- [Installation Instructions](#installation-instructions)
- [Usage Examples](#usage-examples)
  - [Entity Validation](#entity-validation)
  - [Data Export](#data-export)
- [Configuration](#configuration)
- [Application/Use Case](#applicationuse-case)
- [Contributing Guidelines](#contributing-guidelines)
- [License Information](#license-information)
- [Contact](#contact)

---

## Project Overview

DataVault Explorer is a Python-based utility designed to streamline database management and data extraction processes. With support for major databases like Hive, Impala, PostgreSQL, Snowflake, and Oracle, it streamlines entity validation and data extraction processes using simple JSON configuration files.. It offers two primary functionalities:

1. **Entity Validation**: Perform health checks on database schemas or tables by running SELECT queries.
2. **Data Export**: Execute custom queries and export results in CSV or Excel formats.

Key features:
- Intelligent handling of complex queries
- Flexible input configuration via JSON files
- Comprehensive error reporting and status updates
- Validate tables and views across multiple databases.
- Centralized database connection management with support for Hive, Impala, PostgreSQL, Snowflake, and Oracle.

---

## Folder Structure

```
data-vault-explorer/
├── EntityValidator.py
├── TablesToFile.py
├── Input/
│   ├── entity_list.json
│   └── export_table.json
├── Output/
│   ├── Entity_Test_Reports/
│   └── TableFileExport/
└── Utils/
    ├── DBConnection.py
    ├── secrets.json
    └── requirements.txt
```

---

## Installation Instructions

1. Clone the repository:
   ```
   git clone https://github.com/shreyasgadder/data-vault-explorer.git
   cd data-vault-explorer
   ```

2. Install required dependencies:
   ```
   pip install -r Utils/requirements.txt
   ```

3. Configure your database connections in `Utils/secrets.json`.

---

## Usage Examples

### Entity Validation

1. Edit `Input/entity_list.json` to specify the schemas or tables you want to validate.
2. Run the validation:
   ```
   python EntityValidator.py
   ```
3. Check the results in `Output/Entity_Test_Reports/`.

### Data Export

1. Edit `Input/export_table.json` to specify your export queries and options.
2. Run the export:
   ```
   python TablesToFile.py
   ```
3. Find your exported files in `Output/TableFileExport/`.

---

## Configuration

Refer to the instructions in the JSON files in the `Input/` directory for detailed configuration options.

---

## Contributing Guidelines
1. Fork the repository and create your branch:
   ```bash
   git checkout -b feature-branch
   ```
2. Make your changes and commit them:
   ```bash
   git commit -m "Add new feature"
   ```
3. Push to the branch:
   ```bash
   git push origin feature-branch
   ```
4. Create a Pull Request and describe the changes you’ve made.

---

## Application/Use Case

### 1. **Federated Database Validation:** Validate database tables and views across federated systems like Hive, Impala, and PostgreSQL, helping to identify issues due to underlying table changes.

### 2. **Schema Health Monitoring:** Ensure schema integrity by validating all tables in a schema, useful for database migrations, audits, or new installations.

### 3. **Automated Query Validation in ETL Pipelines:** Automate query validation and data export, making the tool a valuable addition to ETL pipelines for smooth data transformation and verification.

### 4. **Database Documentation:** Generate up-to-date reports on database schemas and table structures for documentation purposes.

### 5. **Development and Testing Support:** Quickly validate changes in database structures during application development and testing phases.

### 6. **Data Extraction for Reporting:** Execute complex queries and export results to CSV or Excel, enabling efficient data extraction for reporting and integration with other systems.

### 7. **Data Archiving:** Efficiently export historical data from operational databases to archive storage.

### 8. **Cross-Database Compatibility:** Standardize validation and data extraction across diverse environments, with support for databases like Snowflake, Oracle, and PostgreSQL.

---

## License Information

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue on the GitHub repository or contact me from [Portfolio](https://shreyasgadder.netlify.app/).
