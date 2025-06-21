# Auto Categorize Feature Specification

## Overview
The Auto Categorize feature automatically assigns categories and additional fields to uncategorized transactions based on user-defined rules in a worksheet named "AutoCat".

## AutoCat Worksheet Structure

### Table Requirements
- **Location**: Worksheet named "AutoCat"
- **Format**: Table with header row in the first row
- **Required Column**: `Category` (specifies the category to assign when a rule matches)

### Column Types

#### 1. Required Column
- **Category**: Assigns the specified category to a matching transaction. If empty, only auto-fill values are applied, and the transaction remains uncategorized.

#### 2. Rule Columns (Optional)
- **Purpose**: Define matching criteria for transactions.
- **Naming Pattern**: `[TransactionColumnName] [ComparisonType]`
- **Comparison Types**:
  - `contains`: Case-insensitive partial text match
  - `min`: Numeric value = specified minimum
  - `max`: Numeric value = specified maximum
  - `equals`: Exact match (case-sensitive for text, precise for numbers)
  - `starts with`: Text starts with specified value
  - `ends with`: Text ends with specified value
  - `regex`: Regular expression match
  - `not contains`: Text does not contain specified value
  - `not equals`: Value does not equal specified value
  - `between`: Numeric value within a range (requires two values: min,max)
- **Examples**:
  - `Description Contains`
  - `Amount Min`
  - `Account Equals`

#### 3. Auto-Fill Columns (Optional)
- **Purpose**: Populate additional transaction fields when a rule matches.
- **Naming**: Must match column headers in the transaction table exactly.
- **Behavior**: Ignored if the header does not match a transaction table column.
- **Examples**:
  - `Tags`
  - `Notes`
  - `Full Description`
  - `Account`

## Processing Logic
- **Target**: Only uncategorized transactions in the active transaction table.
- **Evaluation**:
  - Rules are evaluated top-to-bottom.
  - All rule columns in a row must match (AND logic) for the rule to apply.
  - Text comparisons are case-insensitive unless using `equals`. Numeric comparisons use precise decimal matching.
  - Empty rule column values are ignored.
- **Assignment**:
  - The first matching rule assigns its `Category` (if specified) and all auto-fill values.
  - Rules with empty `Category` apply only auto-fill values.
  - Processing stops after the first match.

## Example AutoCat Table

| Category   | Description Contains | Amount Min | Amount Max | Tags      | Notes                          |
|------------|---------------------|------------|------------|-----------|--------------------------------|
| Groceries  | WALMART             |            | 500        | shopping  | Grocery expense                |
| Gas        | SHELL               |            |            | fuel      | Gas station purchase           |
| Salary     | PAYROLL             | 1000       |            | income    | Monthly salary                 |
| Coffee     | STARBUCKS           |            | 20         | beverage  | Coffee purchase                |

## Implementation Requirements

### Validation and Error Handling
- **Pre-Processing**:
  - Verify "AutoCat" worksheet exists.
  - Confirm `Category` column is present.
  - Validate rule column names follow the naming convention.
  - Check auto-fill column headers match transaction table columns.
- **Error Handling**:
  - Skip rules with invalid column references.
  - Log warnings for unrecognized auto-fill columns.
  - Continue processing if individual rules fail.
  - Provide user feedback on validation issues.

### Performance Considerations
- Stop rule evaluation after the first match.
- Cache compiled regex patterns for `regex` rules.
- Batch process transactions for large datasets.
- Optimize for efficient rule matching.

### Data Integrity
- **Assignments**: Overwrite existing fields only for uncategorized transactions.
- **Audit Trail**: Track auto-categorization actions for debugging.

## User Guidelines

### Best Practices
- Place specific rules before general ones.
- Test rules to ensure accurate matching.
- Use clear, consistent category names.
- Review categorization accuracy regularly.
- Backup the worksheet before modifying rules.

### Common Patterns
- **Merchant-Based**: Use `Description Contains` for vendor names.
- **Amount-Based**: Use `Amount Min`/`Max` for expense limits.
- **Account-Specific**: Use `Account Equals` for account-based rules.
- **Combined**: Use multiple conditions for precise matching.