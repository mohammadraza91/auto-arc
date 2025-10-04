# Contributing to Auto ARC

Thank you for your interest in contributing to Auto ARC! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/yourusername/auto-arc/issues) page
- Provide detailed descriptions and steps to reproduce
- Include system information and error messages
- Use appropriate labels (bug, enhancement, documentation)

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and its benefits
- Provide use cases and examples
- Consider implementation complexity

### Code Contributions
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**: `git commit -m 'Add amazing feature'`
6. **Push to your fork**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

## 🛠️ Development Setup

### Prerequisites
- Python 3.10+
- Git
- Google Gemini API key

### Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/auto-arc.git
cd auto-arc

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

### Testing
```bash
# Run basic tests
python -m pytest tests/

# Test specific components
python -c "import streamlit_app; print('Import successful')"
```

## 📝 Code Style

### Python
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small

### Streamlit
- Use consistent naming conventions
- Organize UI components logically
- Add helpful comments for complex layouts
- Ensure responsive design

### Documentation
- Update README.md for new features
- Add docstrings to new functions
- Include examples in documentation
- Keep changelog updated

## 🎯 Areas for Contribution

### High Priority
- **Error Handling**: Improve error messages and recovery
- **Performance**: Optimize code generation speed
- **Testing**: Add comprehensive test coverage
- **Documentation**: Improve user guides and examples

### Medium Priority
- **New Content Types**: Add support for more code types
- **UI/UX**: Enhance user interface and experience
- **Export Options**: Add more output formats
- **Integration**: Connect with more external services

### Low Priority
- **Themes**: Add dark/light mode support
- **Internationalization**: Multi-language support
- **Advanced Features**: Complex code generation patterns
- **Analytics**: Usage tracking and insights

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Operating System
   - Python version
   - Package versions
   - Browser (for UI issues)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Screenshots if applicable

3. **Error Details**
   - Full error messages
   - Stack traces
   - Log files if available

## 🚀 Feature Requests

When suggesting features:

1. **Problem Description**
   - What problem does this solve?
   - Who would benefit from this?
   - Current workarounds

2. **Proposed Solution**
   - How should it work?
   - User interface considerations
   - Technical requirements

3. **Additional Context**
   - Use cases and examples
   - Priority level
   - Implementation complexity

## 📋 Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Clear commit messages

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🏷️ Labels

We use the following labels:

- **bug**: Something isn't working
- **enhancement**: New feature or request
- **documentation**: Improvements to documentation
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention needed
- **priority: high**: High priority items
- **priority: low**: Low priority items

## 💬 Communication

- **GitHub Discussions**: For general questions and ideas
- **Issues**: For bug reports and feature requests
- **Pull Requests**: For code contributions
- **Email**: For security issues (use private channels)

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page
- Special thanks in documentation

## 📜 Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards
- Be respectful and inclusive
- Use welcoming and inclusive language
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Enforcement
Instances of unacceptable behavior may be reported to the project maintainers. All complaints will be reviewed and investigated.

## 📞 Getting Help

- **Documentation**: Check README.md and code comments
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join our community channels

Thank you for contributing to Auto ARC! 🚀
