# Contributing to Rule #1 Investing Platform

Thank you for considering contributing to the Rule #1 Investing Platform! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow:

- **Be respectful** - Treat everyone with respect and courtesy
- **Be collaborative** - Work together and help each other
- **Be inclusive** - Welcome diverse perspectives and backgrounds
- **Be professional** - Keep discussions focused and productive

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+ (or Docker)
- Git

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/rule1-app.git
   cd rule1-app
   ```

2. **Set up with Docker (Recommended)**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Edit .env with your API key
   nano .env
   
   # Start development environment
   make dev
   ```

3. **Or set up manually**
   ```bash
   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python init_db.py
   
   # Frontend setup
   cd ../frontend
   npm install
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

## Development Workflow

### Branch Naming Convention

Use descriptive branch names with prefixes:

- `feature/` - New features (e.g., `feature/watchlist-alerts`)
- `fix/` - Bug fixes (e.g., `fix/database-connection`)
- `docs/` - Documentation (e.g., `docs/api-reference`)
- `chore/` - Maintenance (e.g., `chore/update-dependencies`)
- `test/` - Test additions (e.g., `test/analysis-endpoints`)

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
type(scope): brief description

# Types:
feat: New feature
fix: Bug fix
docs: Documentation changes
style: Code style changes (formatting, etc.)
refactor: Code refactoring
test: Adding or updating tests
chore: Maintenance tasks
perf: Performance improvements
ci: CI/CD changes

# Examples:
feat(backend): add portfolio tracking endpoint
fix(frontend): resolve chart rendering issue
docs(api): update authentication documentation
chore(deps): update fastapi to 0.110.0
```

### Development Process

1. **Make your changes**
   - Write clean, readable code
   - Follow coding standards
   - Add comments for complex logic

2. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   
   # Integration tests
   make test-api
   ```

3. **Lint your code**
   ```bash
   # Backend
   cd backend
   flake8 .
   black .
   isort .
   
   # Frontend
   cd frontend
   npm run lint
   ```

4. **Update documentation**
   - Update README if needed
   - Update API docs for new endpoints
   - Add inline code comments

## Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

```python
# Use type hints
def calculate_sticker_price(eps: float, growth_rate: float) -> float:
    """Calculate intrinsic value using Rule #1 formula.
    
    Args:
        eps: Current earnings per share
        growth_rate: Expected annual growth rate (%)
        
    Returns:
        Calculated sticker price
    """
    future_eps = eps * ((1 + growth_rate / 100) ** 10)
    return future_eps / (1.15 ** 10)

# Use descriptive variable names
user_analyses = db.query(Analysis).filter(Analysis.user_id == user_id).all()

# Keep functions focused and small
# Maximum ~50 lines per function
```

**Tools:**
- `black` - Code formatting
- `flake8` - Linting
- `isort` - Import sorting
- `mypy` - Type checking

### JavaScript/React (Frontend)

**Style Guide:** Airbnb JavaScript Style Guide

```javascript
// Use functional components with hooks
const StockAnalysis = ({ symbol }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchStockData(symbol);
  }, [symbol]);
  
  // Keep components small and focused
  // Extract complex logic into custom hooks
  return (
    <div>
      {loading ? <Loader /> : <DataDisplay data={data} />}
    </div>
  );
};

// Use meaningful component and variable names
const AnalysisSummaryCard = ({ analysis }) => {
  // Component logic
};
```

**Tools:**
- ESLint - Linting
- Prettier - Formatting

### SQL/Database

```sql
-- Use descriptive table and column names
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for frequently queried columns
CREATE INDEX idx_analyses_symbol ON analyses(symbol);

-- Use constraints for data integrity
ALTER TABLE analyses ADD CONSTRAINT chk_meaning_score 
    CHECK (meaning_score >= 1 AND meaning_score <= 5);
```

### Docker

```dockerfile
# Use multi-stage builds
FROM python:3.11-slim as builder
# Build stage...

FROM python:3.11-slim
# Production stage...

# Use specific versions
FROM node:18-alpine

# Minimize layers
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*
```

## Testing Guidelines

### Backend Tests

```python
# tests/test_analysis.py
import pytest
from main import app
from database import get_db

def test_create_analysis(client):
    """Test creating a new analysis."""
    response = client.post(
        "/api/analyses",
        json={
            "symbol": "AAPL",
            "meaning_score": 5,
            "moat_score": 4
        }
    )
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"

def test_get_analysis_not_found(client):
    """Test getting non-existent analysis."""
    response = client.get("/api/analyses/99999")
    assert response.status_code == 404
```

**Requirements:**
- Write tests for new features
- Maintain >80% code coverage
- Test happy path and edge cases
- Mock external API calls

### Frontend Tests

```javascript
// components/StockCard.test.jsx
import { render, screen } from '@testing-library/react';
import StockCard from './StockCard';

describe('StockCard', () => {
  it('renders stock symbol', () => {
    render(<StockCard symbol="AAPL" price={150} />);
    expect(screen.getByText('AAPL')).toBeInTheDocument();
  });
  
  it('displays price correctly', () => {
    render(<StockCard symbol="AAPL" price={150.50} />);
    expect(screen.getByText('$150.50')).toBeInTheDocument();
  });
});
```

### Integration Tests

```bash
# Test the full stack
docker compose up -d
curl http://localhost:8000/ # Backend health
curl http://localhost:3000/ # Frontend health
docker compose down
```

## Submitting Changes

### Pull Request Process

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Push your changes**
   ```bash
   git push origin your-branch
   ```

3. **Create Pull Request**
   - Go to GitHub and create PR
   - Fill out the PR template completely
   - Link related issues
   - Add screenshots if UI changes

4. **Wait for CI checks**
   - All tests must pass
   - Code coverage maintained
   - Docker builds successfully
   - No security vulnerabilities

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No console warnings/errors
- [ ] Tested in Docker environment
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] Self-review completed

## Review Process

### What Reviewers Look For

1. **Code Quality**
   - Readable and maintainable
   - Follows coding standards
   - No code smells

2. **Testing**
   - Adequate test coverage
   - Tests are meaningful
   - Edge cases considered

3. **Documentation**
   - Code is well-commented
   - API docs updated
   - README updated if needed

4. **Security**
   - No security vulnerabilities
   - Input validation
   - No exposed secrets

5. **Performance**
   - No unnecessary queries
   - Efficient algorithms
   - Proper caching

### Addressing Feedback

- Respond to all comments
- Make requested changes
- Push updates to the same branch
- Request re-review when ready

## Areas for Contribution

### High Priority

- [ ] User authentication and authorization
- [ ] Email price alerts
- [ ] Portfolio tracking
- [ ] Technical analysis charts
- [ ] Mobile responsiveness improvements

### Good First Issues

Look for issues labeled `good-first-issue`:
- Documentation improvements
- Bug fixes
- UI enhancements
- Test coverage improvements

### Feature Requests

Check the issues labeled `enhancement` for community-requested features.

## Community

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and general discussion
- **Pull Requests** - Code reviews and feedback

### Getting Help

- Read the documentation in `/docs`
- Check existing issues and PRs
- Ask questions in GitHub Discussions
- Review the code and tests

## Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes
- Recognized in the contributors graph

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Rule #1 Investing Platform! 🚀
