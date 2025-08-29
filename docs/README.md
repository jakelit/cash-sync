# Cash Sync Documentation

This directory contains comprehensive documentation for the Cash Sync application, including architecture documentation, testing standards, and user guides.

## 📚 Documentation Overview

This directory contains comprehensive documentation for the Cash Sync application:

### **Core Documentation**
- **[Architecture](architecture.md)**: Complete system architecture and design patterns
- **[Architecture Standards](architecture-standards.md)**: Centralized architectural standards and requirements
- **[ADRs](adrs/)**: Architecture Decision Records with historical context
- **[Testing Standards](testing-standards/)**: Comprehensive testing guidelines and templates

### **User Guides**
- **[Transaction Import](import_transactions.md)**: How to import bank transactions
- **[Auto-Categorization](auto_categorize.md)**: Automatic transaction categorization

### **Development Resources**
- **[Test Plans](test-plans/)**: Component-specific test plans
- **[Specifications](specs/)**: Feature specifications and requirements
- **[AI Prompts](prompts/)**: Templates for AI-assisted development

> 💡 **Tip**: Use `find docs/ -name "*.md"` to see all documentation files, or browse the directory structure directly.

## 🏗️ Architecture Documentation

### [architecture.md](./architecture.md)
Complete system architecture documentation including:
- **System Overview**: High-level architecture and principles
- **Component Documentation**: Detailed description of each component
- **Data Flow**: How data moves through the system
- **Design Patterns**: Patterns used in the implementation
- **Performance Characteristics**: System performance considerations
- **Security Considerations**: Security measures and best practices

### [architecture-standards.md](./architecture-standards.md)
Centralized architectural standards and requirements:
- **Code Standards**: PEP 8, type hints, documentation requirements
- **Testing Standards**: Coverage requirements and testing patterns
- **Error Handling**: Consistent error handling patterns
- **Security Standards**: Input validation and security requirements
- **Performance Standards**: Performance characteristics and requirements

### [adrs/](./adrs/)
Architecture Decision Records (ADRs) documenting key architectural decisions:
- **Layered Architecture Pattern**: Why we chose a layered approach
- **Abstract Base Class for Importers**: Design pattern for bank importers
- **Excel Table-Based Storage**: Data storage strategy
- **Tkinter GUI Framework**: GUI technology choice
- **Pandas Data Processing**: Data processing library selection

## 🧪 Testing Standards

### [testing-standards/](./testing-standards/)
Comprehensive testing standards and guidelines:
- **Coverage Requirements**: See [Coverage Requirements](testing-standards/tools-and-automation/coverage_requirements.md) for official thresholds
- **Test Organization**: How to structure and organize tests
- **Implementation Guidelines**: Coding standards for tests
- **Tools and Automation**: CI/CD integration and testing tools

## 📖 User Guides

### [import_transactions.md](./import_transactions.md)
Complete guide for importing bank transactions:
- **Supported Banks**: Ally Bank and Capital One
- **File Requirements**: CSV format specifications
- **Step-by-Step Instructions**: How to import transactions
- **Troubleshooting**: Common issues and solutions

### [auto_categorize.md](./auto_categorize.md)
Guide for automatic transaction categorization:
- **Rule Configuration**: How to set up categorization rules
- **Pattern Matching**: Understanding the matching system
- **Best Practices**: Tips for effective categorization
- **Troubleshooting**: Common categorization issues

## 🎯 How to Use This Documentation

### For Developers
1. **Start with Architecture**: Read `architecture.md` to understand the system
2. **Review ADRs**: Check `adrs/` for relevant architectural decisions
3. **Follow Testing Standards**: Use `testing-standards/` for all testing work
4. **Create Test Plans**: Use the template in `testing-standards/test-plan-template.md`

### Discovering Documentation
```bash
# Find all documentation files
find docs/ -name "*.md" -type f

# Find documentation by topic
find docs/ -name "*test*" -o -name "*arch*"

```

### For AI Assistants
1. **Reference Architecture**: Always consider architectural implications
2. **Check ADRs**: Review relevant ADRs before making architectural changes
3. **Follow Testing Standards**: Use testing standards for all test-related work
4. **Update Documentation**: Create ADRs for significant architectural decisions

### For Users
1. **Import Transactions**: Follow `import_transactions.md`
2. **Auto-Categorize**: Use `auto_categorize.md` for categorization
3. **Troubleshooting**: Check user guides for common issues

## 🔄 Documentation Maintenance

### When to Update Documentation
- **Architecture Changes**: Update `architecture.md` and create new ADRs
- **New Features**: Update relevant user guides and specifications
- **Testing Changes**: Update testing standards and test plans
- **Bug Fixes**: Update troubleshooting sections in user guides

### Documentation Standards
- **Markdown Format**: All documentation uses Markdown
- **Clear Structure**: Use consistent headings and organization
- **Code Examples**: Include relevant code examples where helpful
- **Cross-References**: Link between related documentation
- **Regular Review**: Review and update documentation regularly

## 📋 Quick Reference

### Architecture Quick Start
```bash
# Read the main architecture
docs/architecture.md

# Check relevant ADRs
docs/adrs/README.md

# Follow testing standards
docs/testing-standards/testing_standards_readme.md
```

### Testing Quick Start
```bash
# Use test plan template
docs/testing-standards/test-plan-template.md

# Follow implementation guide
docs/testing-standards/test-implementation-guide.md

# Check coverage requirements
docs/testing-standards/tools-and-automation/coverage-requirements.md
```

### User Quick Start
```bash
# Import transactions
docs/import_transactions.md

# Auto-categorize transactions
docs/auto_categorize.md
```

## 🤝 Contributing to Documentation

### Creating New Documentation
1. **Follow Structure**: Use existing documentation as templates
2. **Cross-Reference**: Link to related documentation
3. **Review**: Have documentation reviewed by team members
4. **Update Index**: Update this README when adding new documentation

### Updating Existing Documentation
1. **Check Impact**: Consider impact on related documentation
2. **Maintain Consistency**: Follow existing style and format
3. **Version Control**: Use meaningful commit messages
4. **Test Changes**: Verify documentation accuracy

## 📞 Support

For questions about documentation:
- **Architecture Questions**: Review `architecture.md` and relevant ADRs
- **Testing Questions**: Check `testing-standards/` documentation
- **User Questions**: Refer to user guides in the root of `docs/`
- **General Questions**: Check the main project README.md

---

**Remember**: Good documentation is as important as good code. Keep it updated, clear, and accessible to all team members.
