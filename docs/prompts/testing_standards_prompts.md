# AI Prompts Guide for Testing Standards

This guide provides ready-to-use prompts for working with AI agents when following our testing standards. All prompts reference our documentation in `docs/testing-standards/` for consistent, high-quality results.

## 📋 How to Use This Guide

1. **Copy the relevant prompt** from the sections below
2. **Replace placeholders** like `[ClassName]`, `[module_name]`, etc. with actual values
3. **Paste into your AI agent** (Claude, ChatGPT, etc.)
4. **The AI will reference our standards** for consistent output

## 🔍 Test Analysis and Review Prompts

### Code Review and Quality Assessment

```
Review this test file against our testing standards in docs/testing-standards/. 
Identify gaps, suggest improvements, and check compliance with our implementation guide.
```

```
Analyze the test coverage for [module_name] and suggest additional test cases 
based on our coverage requirements in docs/testing-standards/coverage-requirements.md
```

```
This test is failing intermittently. Review it against our testing standards 
and suggest fixes for reliability issues.
```

```
Audit this test suite for compliance with our testing standards. Focus on 
naming conventions, assertion patterns, and fixture usage from 
docs/testing-standards/test-implementation-guide.md
```

```
Compare this legacy test code with our current standards and provide a 
gap analysis with prioritized improvement recommendations.
```

### Test Refactoring

```
Refactor these legacy tests to follow our current testing standards. 
Focus on fixture usage, assertion patterns, and organization from 
docs/testing-standards/test-implementation-guide.md
```

```
Convert these manual test scenarios into automated tests following our 
test plan template and implementation standards.
```

```
Modernize this test suite to use pytest best practices as defined in our 
testing standards documentation.
```

```
Reorganize this test file structure to match our testing standards for 
test class organization and method naming.
```

## 🔧 Implementation and Development Prompts

### Test Plan Creation

```
Create a test plan for the [ClassName] class following our testing standards 
in docs/testing-standards/test-plan-template.md.

The class is located at: [file_path]
Key functionality includes: [brief description]
```

```
Generate a comprehensive test plan for [feature_name] that covers all user 
stories and follows our testing standards in docs/testing-standards/test-plan-template.md.
```

```
Create a test plan for this API endpoint following our testing standards. 
Include security, performance, and integration testing considerations.
```

### Test Implementation

```
Implement comprehensive tests for the [ClassName] class. Use the test plan 
at docs/test-plans/test_plan_[class_name].md and follow our implementation standards.
```

```
Create property-based tests for [function_name] using hypothesis, following 
the patterns in our testing standards documentation.
```

```
Write integration tests for [feature_name] that mock external dependencies 
according to our mocking strategies in docs/testing-standards/
```

```
Implement unit tests for this [component_type] following our Arrange-Act-Assert 
pattern and fixture guidelines from docs/testing-standards/test-implementation-guide.md
```

```
Create parameterized tests for [function_name] that cover edge cases and 
boundary conditions as specified in our testing standards.
```

### Fixture and Utility Creation

```
Create reusable test fixtures for [domain_area] following our fixture patterns 
in docs/testing-standards/test-implementation-guide.md
```

```
Design a test data factory for [entity_type] that generates realistic test data 
while following our test data strategy guidelines.
```

```
Build a mock strategy for [external_service] integration following our 
mocking patterns and best practices.
```

```
Create shared conftest.py fixtures for [project_area] that other test modules 
can reuse according to our standards.
```

## 🚀 CI/CD and Automation Prompts

### Pipeline Configuration

```
Set up a GitHub Actions workflow for this project following our CI/CD standards 
in docs/testing-standards/tools-and-automation/ci-cd-integration.md
```

```
Configure pytest and coverage settings for this new project using our 
standard configuration from docs/testing-standards/pytest-configuration.md
```

```
Create pre-commit hooks for this repository that enforce our testing standards 
and quality gates.
```

```
Design a CI/CD pipeline that runs different test types (unit, integration, e2e) 
according to our testing standards and performance requirements.
```

```
Set up automated test reporting and notifications following our CI/CD 
integration guidelines.
```

### Coverage and Quality Gates

```
Analyze our current test coverage and create an action plan to meet the 
thresholds defined in docs/testing-standards/coverage-requirements.md
```

```
Set up coverage reporting and quality gates for our CI pipeline based on 
our coverage standards.
```

```
Configure SonarQube integration following our quality gate requirements 
and coverage standards.
```

```
Create a coverage enforcement strategy that aligns with our CI/CD pipeline 
and testing standards.
```

## 📊 Analysis and Reporting Prompts

### Test Metrics and Insights

```
Generate a test health report for this project, comparing our current state 
against the standards in docs/testing-standards/
```

```
Analyze our test execution times and suggest optimizations based on 
our performance testing guidelines.
```

```
Review our test failure patterns from the last month and suggest improvements 
to test reliability using our standards as a baseline.
```

```
Create a dashboard of testing metrics that tracks compliance with our 
testing standards over time.
```

```
Identify test suite bottlenecks and suggest improvements following our 
performance optimization guidelines.
```

### Strategic Planning

```
Create a testing roadmap for Q[X] that aligns with our testing standards and 
addresses current gaps in coverage and quality.
```

```
Evaluate our current testing practices against industry best practices and 
our internal standards. Suggest an improvement plan.
```

```
Design a testing strategy for [new_project] that incorporates all aspects 
of our testing standards from day one.
```

```
Create a technical debt reduction plan for our test suite based on our 
current standards and quality requirements.
```

## 🎯 Project-Specific Prompts

### New Project Setup

```
Bootstrap testing infrastructure for a new [project_type] project following 
our complete testing standards in docs/testing-standards/
```

```
Create a testing checklist for this sprint's features based on our 
test plan template and quality requirements.
```

```
Set up initial project structure for testing including directories, 
configuration files, and basic fixtures following our standards.
```

```
Create project-specific testing guidelines that extend our base standards 
for [specific_technology/domain].
```

### Legacy Code Improvement

```
Create a migration plan to bring this legacy codebase up to our current 
testing standards, prioritizing high-risk areas.
```

```
Design a strategy to add tests to this untested legacy module while 
following our standards for new code coverage requirements.
```

```
Assess this legacy system and create a phased approach to implement 
our testing standards without disrupting current functionality.
```

```
Create characterization tests for this legacy component that can serve 
as a foundation for refactoring to our current standards.
```

## 🔬 Specialized Testing Prompts

### Security Testing

```
Create security-focused tests for [feature] following the security testing 
patterns in our implementation guide.
```

```
Review this authentication module and create comprehensive security tests 
based on our testing standards.
```

```
Design input validation tests for [API/form] that cover security vulnerabilities 
and follow our security testing guidelines.
```

```
Implement authorization tests for [feature] that verify access controls 
according to our security testing standards.
```

### Performance Testing

```
Design performance tests for [component] using pytest-benchmark, following 
our performance testing guidelines in docs/testing-standards/
```

```
Create load tests for this API endpoint that align with our performance 
testing standards and benchmarking practices.
```

```
Implement memory usage tests for [component] following our performance 
testing patterns and measurement guidelines.
```

```
Design scalability tests for [system] that validate performance requirements 
according to our testing standards.
```

### Property-Based Testing

```
Identify functions in [module] that would benefit from property-based testing 
and implement them using hypothesis following our standards.
```

```
Convert these example-based tests to property-based tests while maintaining 
coverage and following our implementation patterns.
```

```
Create property-based tests for [data_structure/algorithm] that verify 
mathematical properties and invariants.
```

```
Design hypothesis strategies for [domain_object] that generate realistic 
test data following our property-based testing guidelines.
```

## 🏗️ Architecture and Design Prompts

### Test Architecture

```
Design a testing strategy for this microservices architecture that follows 
our integration testing standards and mocking strategies.
```

```
Create a test organization plan for this large codebase that aligns with 
our testing standards and supports team collaboration.
```

```
Design test boundaries and interfaces for [system] that follow our 
integration testing and mocking guidelines.
```

```
Create a testing architecture for [distributed_system] that maintains 
test isolation while following our standards.
```

### Test Data Management

```
Design a test data management strategy for this project that follows our 
test data guidelines and supports both unit and integration testing.
```

```
Create database fixtures and factories for this data model following 
our testing standards for database testing.
```

```
Implement test data seeding and cleanup strategies that align with our 
testing standards and isolation requirements.
```

```
Design a test data versioning strategy for [complex_domain] that supports 
our testing standards and team collaboration.
```

## 📚 Documentation and Training Prompts

### Team Education

```
Create a training presentation on our testing standards for new team members, 
highlighting key practices and common pitfalls.
```

```
Generate examples of good vs bad tests based on our testing standards 
to use in code review training.
```

```
Create a quick reference guide for our testing standards that developers 
can use during daily development.
```

```
Design interactive examples that teach our testing patterns and standards 
through hands-on coding exercises.
```

### Documentation Maintenance

```
Review and update our testing standards documentation based on recent 
lessons learned and industry best practices.
```

```
Create troubleshooting guides for common testing issues teams encounter 
when following our standards.
```

```
Generate FAQ documentation for our testing standards based on common 
questions and implementation challenges.
```

```
Create migration guides for teams adopting our testing standards from 
other testing approaches.
```

## 🔄 Maintenance and Evolution Prompts

### Standards Evolution

```
Evaluate new testing tools and frameworks against our current standards 
and recommend updates to our testing stack.
```

```
Review our testing standards quarterly assessment and suggest improvements 
based on team feedback and industry trends.
```

```
Assess the impact of [new_technology] on our testing standards and 
recommend necessary updates or additions.
```

```
Create a standards evolution plan that maintains backward compatibility 
while adopting new best practices.
```

### Continuous Improvement

```
Analyze our test maintenance burden and suggest automation improvements 
that align with our testing standards.
```

```
Identify technical debt in our test suite and create a remediation plan 
following our current standards.
```

```
Review test execution efficiency and suggest optimizations that maintain 
our quality standards while improving speed.
```

```
Create metrics and monitoring for our testing standards compliance 
and suggest improvement processes.
```

## 💡 Context-Aware Prompts

### Project Context Integration

```
Given our current sprint goals, create a testing plan that follows our 
standards and ensures adequate coverage for the new features.
```

```
Review the test gaps in our [specific_domain] module and prioritize 
improvements based on business criticality and our coverage standards.
```

```
Create testing acceptance criteria for [user_story] that align with our 
testing standards and quality requirements.
```

```
Design a testing approach for [critical_feature] that exceeds our standard 
requirements due to its business importance.
```

### Team-Specific Prompts

```
Create a testing onboarding checklist for our new [role] developer 
that covers our standards and team-specific practices.
```

```
Generate testing guidelines for our junior developers that simplify 
our comprehensive standards into actionable steps.
```

```
Create role-specific testing responsibilities that align with our 
standards and team structure.
```

```
Design a mentoring program for testing practices that reinforces our 
standards through peer learning.
```

## 🎨 Creative and Advanced Prompts

### Innovation and Experimentation

```
Suggest innovative testing approaches for [complex_problem] that extend 
our current standards while maintaining quality principles.
```

```
Design experiments to validate new testing techniques against our 
current standards and success metrics.
```

```
Create proof-of-concept tests for [emerging_technology] that could be 
integrated into our testing standards.
```

```
Explore AI-assisted testing approaches that could enhance our current 
standards and development workflow.
```

### Cross-Functional Integration

```
Design testing approaches that integrate with our design system and 
follow our testing standards for UI components.
```

```
Create testing strategies for [business_process] that involve multiple 
teams while maintaining our quality standards.
```

```
Design API contract testing that aligns with our testing standards 
and supports multiple consuming teams.
```

```
Create testing approaches for data pipelines that follow our standards 
and ensure data quality throughout the system.
```

## 📞 Support and Troubleshooting Prompts

### Problem Diagnosis

```
This test is flaky and fails intermittently. Analyze it against our 
testing standards and suggest fixes for improved reliability.
```

```
Our test suite is running too slowly. Review it against our performance 
guidelines and suggest optimizations.
```

```
We're having trouble mocking [external_service]. Suggest approaches that 
follow our mocking strategies and patterns.
```

```
Our coverage is dropping despite adding tests. Analyze our approach 
against our coverage standards and suggest improvements.
```

### Best Practice Application

```
We need to test [complex_scenario]. Design an approach that follows our 
testing standards while handling the complexity effectively.
```

```
How should we adapt our testing standards for [special_case] while 
maintaining our quality principles?
```

```
Create guidelines for testing [specific_pattern] that extend our base 
standards with domain-specific considerations.
```

```
Design a testing approach for [edge_case] that maintains compliance with 
our standards while addressing unique requirements.
```

---

## 💡 Tips for Effective Prompt Usage

### Prompt Customization
- **Replace placeholders** with specific names, paths, and contexts
- **Add relevant details** about your specific situation
- **Combine prompts** when you need multiple perspectives
- **Follow up** with clarifying questions based on the AI's response

### Getting Better Results
- **Be specific** about which standards documents are most relevant
- **Provide context** about your project, technology stack, and constraints
- **Ask for examples** when you need concrete implementation guidance
- **Request explanations** of how suggestions align with your standards

### Iterative Improvement
- **Review outputs** against your actual standards documentation
- **Refine prompts** based on the quality of responses you receive
- **Share successful prompts** with your team for consistency
- **Update this guide** as you discover new effective prompt patterns

---

**Remember**: These prompts are designed to work with your testing standards documentation. Always verify that AI-generated outputs align with your specific requirements and quality expectations.