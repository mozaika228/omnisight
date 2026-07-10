# Contributing to OmniSight

Thank you for your interest in contributing to OmniSight! We appreciate your help in making this project better.

## Code of Conduct

Please be respectful and constructive in all interactions with other contributors and maintainers.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in [GitHub Issues](https://github.com/omnisight/omnisight/issues)
2. Create a new issue with a clear title and description
3. Include steps to reproduce (for bugs)
4. Include your environment details (OS, Python version, GPU info)

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/omnisight.git
   cd omnisight
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Make your changes**
   - Follow PEP 8 style guide
   - Add tests for new functionality
   - Update documentation as needed

5. **Run tests and linting**
   ```bash
   pytest tests/
   black . && isort .
   flake8 . && pylint .
   mypy .
   ```

6. **Commit your changes**
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**
   - Provide a clear description of your changes
   - Reference any related issues
   - Wait for review and address feedback

## Development Guidelines

### Code Style

- **Python:** PEP 8, Black formatter (100 char line length)
- **TypeScript/JavaScript:** Prettier + ESLint
- **Commit Messages:** Clear, descriptive, present tense

### Project Structure

```
omnisight/
├── apps/          # Applications (API, Web)
├── services/      # Microservices
├── packages/      # Shared packages
├── docs/          # Documentation
└── tests/         # Test suites
```

### Adding a New Feature

1. Create feature branch
2. Add documentation (docstrings, README updates)
3. Add unit tests
4. Add integration tests
5. Update ROADMAP.md if it's a planned feature
6. Submit PR with description

### Testing

All contributions should include tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=apps --cov=services

# Run integration tests
pytest tests/integration/
```

### Documentation

- Update docstrings in code
- Update README.md for user-facing changes
- Update relevant doc files (ARCHITECTURE.md, API.md, etc.)
- Add comments for complex logic

## Review Process

1. All PRs require at least one review
2. Tests must pass (CI/CD pipeline)
3. Code coverage should not decrease
4. Documentation must be updated
5. Commit history should be clean (consider squashing commits)

## Getting Help

- **Questions?** Open a [Discussion](https://github.com/omnisight/omnisight/discussions)
- **Want to chat?** Join our [Community Discord](#)
- **Found a bug?** Open an [Issue](https://github.com/omnisight/omnisight/issues)

## Areas for Contribution

We're especially looking for help with:

- ✅ Documentation improvements
- ✅ Bug fixes
- ✅ Performance optimizations
- ✅ Test coverage
- ✅ New AI models integration
- ✅ Mobile app development
- ✅ Cloud deployment guides
- ✅ Language/localization support

## License

By contributing to OmniSight, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to making OmniSight better! 🎉

