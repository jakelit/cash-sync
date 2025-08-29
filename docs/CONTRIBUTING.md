# Contributing to Cash Sync

We love your input! We want to make contributing to Cash Sync as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## We Develop with Github
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [Github Flow](https://guides.github.com/introduction/flow/index.html)
Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. Review our [Architecture Standards](architecture-standards.md) to understand requirements.
3. If you've added code that should be tested, add tests following our [testing standards](testing-standards/).
4. If you've changed APIs, update the documentation.
5. Ensure the test suite passes and meets [coverage requirements](testing-standards/tools-and-automation/coverage_requirements.md).
6. Make sure your code follows our [coding standards](architecture-standards.md).
7. Issue that pull request!

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issue tracker](https://github.com/jakelit/cash-sync/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/jakelit/cash-sync/issues/new); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Use a Consistent Coding Style

### Code Standards
* Follow our [Architecture Standards](architecture-standards.md) for comprehensive coding standards
* Use [Black](https://github.com/psf/black) for code formatting
* Use [Pylint](https://pylint.pycqa.org/) for linting
* Use [MyPy](https://mypy.readthedocs.io/) for type checking

### DRY Principle (Don't Repeat Yourself)
We follow the DRY principle to maintain consistency and reduce maintenance overhead:

* **Single Source of Truth**: Each standard, requirement, or architectural decision is defined in exactly one place
* **Reference, Don't Duplicate**: When documentation needs to mention standards, reference the single source rather than copying content
* **Key Single Sources**:
  - **Coverage Requirements**: [coverage_requirements.md](testing-standards/tools-and-automation/coverage_requirements.md)
  - **Architectural Standards**: [architecture-standards.md](architecture-standards.md)
  - **Architecture Decisions**: [ADRs](adrs/)
  - **Testing Standards**: [testing-standards/](testing-standards/)

* **Before Adding Content**: Check if the information already exists in one of our single sources of truth
* **When Updating Standards**: Update only the single source, then update any references to point to the updated source

### Testing Requirements
* All code must meet our [coverage requirements](testing-standards/tools-and-automation/coverage_requirements.md)
* Follow testing patterns in [Architecture Standards](architecture-standards.md)
* Use test plan templates from [testing-standards](testing-standards/)

### Architecture Compliance
* Review [architecture.md](architecture.md) to understand the system design
* Ensure your changes align with our layered architecture
* Follow design patterns documented in our [ADRs](adrs/)

## Documentation Standards

When contributing code, please ensure your documentation follows our standards:

* **Code Documentation**: Follow docstring standards in [Architecture Standards](architecture-standards.md)
* **Architecture Changes**: Create ADRs for significant architectural decisions (see [ADR Guidelines](adrs/README.md))
* **User Documentation**: Update relevant user guides if functionality changes
* **API Changes**: Update API documentation and ensure backward compatibility

## Quality Assurance

Before submitting your contribution:

* **Follow the DRY Principle**: Ensure no duplication of standards, requirements, or architectural decisions across documentation
  - Coverage requirements are defined only in [coverage_requirements.md](testing-standards/tools-and-automation/coverage_requirements.md)
  - Architectural standards are defined only in [architecture-standards.md](architecture-standards.md)
  - Reference these single sources of truth rather than duplicating content
* Verify coverage meets our [official requirements](testing-standards/tools-and-automation/coverage_requirements.md)
* Ensure all tests pass and follow our [testing patterns](testing-standards/)
* Review your code against our [Architecture Standards](architecture-standards.md) checklist

## License
By contributing, you agree that your contributions will be licensed under its MIT License. 