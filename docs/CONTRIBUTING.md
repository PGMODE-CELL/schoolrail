# SchoolRail Contribution Guide

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/schoolrail.git`
3. Create a feature branch: `git checkout -b feature/your-feature`

## Development Workflow

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Development
```bash
cd admin
npm install
npm run dev
```

## Code Standards

### Python
- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Maximum line length: 100

### JavaScript/TypeScript
- Use ESLint
- Follow Prettier formatting
- Use TypeScript strict mode

##提交规范

- Use clear commit messages
- Reference issues in commits
- Squash related commits

## Testing

Run tests before submitting:
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
cd admin && npm test
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit PR with description