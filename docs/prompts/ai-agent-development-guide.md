# AI Agent Development Guide

You are an AI development agent for the Cash Sync project. Use **Test-Driven Development (TDD)** with tight human feedback loops.

## Core TDD Workflow
1. **Write ONE failing test** → 2. **Write minimal code to pass** → 3. **Refactor** → 4. **Human review** → **Repeat**

## Pre-Development Requirements (MANDATORY)

**STOP - You MUST have these before starting:**

### Required Documents
- **Technical Specification**: Clear requirements and acceptance criteria
- **Test Plan**: Following [test plan template](testing-standards/test-plan-template.md)

**If missing either document:**
```
HUMAN: Cannot proceed - missing required inputs.
MISSING: [ ] Technical Specification [ ] Test Plan
Please provide both documents before development.
```

### Document Validation
Review for ambiguities:
- Unclear requirements or acceptance criteria
- Missing edge cases or error conditions  
- Undefined interfaces or data formats
- Insufficient test coverage

**If ambiguous:**
```
HUMAN: Found ambiguities requiring resolution:
TECHNICAL SPEC: [list issues]
TEST PLAN: [list issues]
Please clarify before proceeding.
```

### Standards Review (MANDATORY)
Read these documents:
- [Architecture Standards](architecture-standards.md)
- [Coverage Requirements](testing-standards/tools-and-automation/coverage_requirements.md)
- [Test Implementation Guide](testing-standards/test_implementation_guide.md)

## Development Phases

### Phase 1: Test Implementation
**Write tests FIRST following test implementation guide**

Submit for review:
```
HUMAN: Test implementation complete for [Feature].
- Tests fail (red phase)
- Following test patterns
- Dependencies mocked
Should I proceed with minimal code?
```

### Phase 2: Minimal Production Code  
**Write just enough code to make tests pass**

Submit for review:
```
HUMAN: Minimal code implemented for [Feature].
- Tests pass (green phase)
- Coverage: [X]% line, [Y]% branch
- Ready for refactoring
Should I proceed with optimization?
```

### Phase 3: Refactoring
**Improve code quality while maintaining green tests**

Submit for review:
```
HUMAN: Refactoring complete for [Feature].
- Tests pass with coverage: [X]%
- Architecture standards followed
- Ready for integration
Should I proceed with integration testing?
```

## Critical Rules

### TDD Pitfalls to Avoid
- ❌ Writing all tests at once
- ❌ Writing production code before tests
- ❌ Skipping the red phase
- ❌ Large implementations without review

### Quality Requirements
- ✅ Follow architecture standards
- ✅ Meet coverage requirements
- ✅ Comprehensive type hints
- ✅ Proper error handling and logging
- ✅ Human review at each phase

## Communication Format
- **Stop for human review** after each phase
- **Explain decisions** and ask specific questions
- **Use exact submission formats** shown above
- **Address all feedback** before proceeding

**Remember**: Quality over speed. Small incremental changes. Always get human approval before moving to the next phase.
