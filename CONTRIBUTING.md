# Contributing to SchoolRail

Thank you for your interest in contributing to SchoolRail!

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating,
you are expected to uphold this code.

## How to Contribute

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/schoolrail.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Commit** your changes: `git commit -m 'Add amazing feature'`
6. **Push** to your branch: `git push origin feature/amazing-feature`
7. **Create** a Pull Request using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
# Runs on http://localhost:3001
```

### Admin Panel Setup
```bash
cd admin
npm install
npm run dev
# Runs on http://localhost:3000
```

### Mobile Apps Setup
```bash
cd parent-app   # or driver-app
npm install
npx expo start
```

## Code Style

- **Python**: Follow PEP 8 — run `ruff check app/` before committing
- **TypeScript/React**: Use Prettier for formatting
- **Commits**: Write meaningful commit messages referencing issues when relevant

## Testing

```bash
# Backend
cd backend
pytest tests/ -v

# Admin
cd admin
npm run lint
npx tsc --noEmit
```

## Pull Request Process

1. Ensure your code passes linting and type-checking
2. Update documentation if you introduce new features or change behavior
3. Make sure your PR description clearly describes the change and motivation
4. A maintainer will review and merge once approved

## Reporting Issues

- **Bugs**: Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Features**: Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- **Security**: See [SECURITY.md](SECURITY.md)

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
