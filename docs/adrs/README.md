# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the Cash Sync application. ADRs are short text documents that capture important architectural decisions made during the development of the application.

## What are ADRs?

Architecture Decision Records are documents that capture important architectural decisions along with their context, consequences, and rationale. They serve as a historical record of why certain architectural choices were made.

## ADR Format

Each ADR follows this structure:

- **Title**: A short, descriptive title
- **Status**: Proposed, Accepted, Deprecated, Superseded, or Rejected
- **Context**: The situation that led to the decision
- **Decision**: The architectural decision that was made
- **Consequences**: The resulting context after applying the decision
- **Compliance**: How this decision aligns with our testing and coding standards

## ADR Naming Convention

ADRs are named using the format: `{number}-{title}.md`

Example: `001-layered-architecture.md`

### Numbering System
- **Sequential numbering**: ADRs are numbered sequentially (001, 002, 003, etc.)
- **Descriptive titles**: Use kebab-case for readability
- **No dates**: Git provides complete version history and timestamps

### Benefits of This Approach
- **Clean filenames**: Easier to read and reference
- **Stable references**: Numbers don't change when files are moved
- **Git history**: Complete temporal information available via `git log`
- **Simpler maintenance**: No need to manage dates in filenames

## Current ADRs

- [ADR-001: Layered Architecture Pattern](001-layered-architecture.md)
- [ADR-002: Abstract Base Class for Importers](002-abstract-base-importer.md)
- [ADR-003: Excel Table-Based Data Storage](003-excel-table-storage.md)
- [ADR-004: Tkinter GUI Framework](004-tkinter-gui-framework.md)
- [ADR-005: Pandas for Data Processing](005-pandas-data-processing.md)
- [ADR-006: Error Handling Strategy](006-error-handling-strategy.md)
- [ADR-007: Logging Strategy](007-logging-strategy.md)

## Creating New ADRs

When making significant architectural decisions:

1. Create a new ADR file using the naming convention
2. Follow the standard ADR format
3. Reference relevant testing standards and compliance requirements
4. Update this README to include the new ADR
5. Consider the impact on existing architecture and testing

## ADR Review Process

1. **Proposed**: Initial ADR created for review
2. **Accepted**: ADR approved and implemented
3. **Deprecated**: ADR no longer relevant but kept for historical context
4. **Superseded**: ADR replaced by a newer decision
5. **Rejected**: ADR not accepted

## Integration with Testing Standards

All ADRs should consider and document:

- Impact on testing strategy
- Compliance with coverage requirements
- Integration with existing test patterns
- Performance implications for testing
- Security considerations for test data

## References

- [Architecture Documentation](../architecture.md)
- [Testing Standards](../testing-standards/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [ADR Tools and Templates](https://adr.github.io/)
