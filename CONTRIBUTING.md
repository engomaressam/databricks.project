# Contributing to Databricks Lakehouse Fitness Pipeline

Thank you for your interest in contributing! This is a portfolio project, but feedback and suggestions are always welcome.

## 📋 Ways to Contribute

### 1. Report Issues
- Found a bug? Open an issue with details
- Have a question? Use GitHub Discussions
- Suggest improvements? Create a feature request

### 2. Improve Documentation
- Fix typos or unclear explanations
- Add examples or use cases
- Translate documentation (if multilingual support added)

### 3. Submit Code Improvements
- Performance optimizations
- Code quality enhancements
- Additional test cases

## 🔧 Development Setup

### Prerequisites
```bash
Python 3.10+
Databricks workspace (free tier works)
Git
```

### Local Setup
```bash
# Clone repository
git clone https://github.com/engomaressam/databricks.project.git
cd databricks.project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Databricks credentials
cat > ~/.databrickscfg << EOF
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = your-access-token
EOF
```

## 📝 Coding Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions small and focused

### Notebook Best Practices
- Add markdown cells for documentation
- Include cell descriptions
- Show sample outputs
- Handle errors gracefully

### SQL Style
- Use uppercase for keywords (SELECT, FROM, WHERE)
- Proper indentation
- Meaningful aliases
- Comments for complex logic

## 🧪 Testing

### Before Submitting
- [ ] Code runs without errors
- [ ] Notebook cells execute in order
- [ ] Documentation is updated
- [ ] No sensitive data (tokens, passwords) in code
- [ ] Git commit messages are descriptive

### Test Data
- Use sample data from `CapstoneProject/Data Set/`
- Generate synthetic data for testing
- Don't commit large data files

## 📤 Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description"
   ```
5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request**
   - Describe what changed
   - Reference any related issues
   - Include screenshots if UI changes

## 🎯 Commit Message Guidelines

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples
```
feat(pipeline): Add streaming support for real-time ingestion

Implemented structured streaming for kafka_multiplex_bz table
with checkpoint management and exactly-once semantics.

Closes #15
```

```
docs(readme): Update installation instructions

Added troubleshooting section and clarified Unity Catalog setup.
```

## 🐛 Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Run notebook '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- Databricks Runtime: [e.g., 14.3 LTS]
- Python version: [e.g., 3.10]
- Cluster configuration: [e.g., 2 workers, i3.xlarge]

**Additional context**
Any other relevant information.
```

## ✨ Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other approaches you've thought about.

**Additional context**
Mockups, examples, or related issues.
```

## 📜 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project

### Not Acceptable
- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Unprofessional conduct

## 🙏 Recognition

Contributors will be acknowledged in:
- README.md Contributors section
- Release notes for significant contributions
- Project documentation

## 📞 Questions?

- Open a GitHub Discussion
- Email: omaressamrme@outlook.com
- LinkedIn: [Connect with me](https://linkedin.com/in/your-profile)

---

Thank you for helping make this project better! 🚀
