# Contributing to SuperNanno

Thank you for considering contributing to **SuperNanno**!  
We welcome contributions that help maintain the project's core values: **reliability**, **clean architecture**, **developer experience**, and **professional quality**.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Architecture Guidelines](#architecture-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Style Guide](#style-guide)

---

## Code of Conduct

By participating in this project, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md) (if available) and treat all contributors with respect.

---

## Getting Started

### 1. Fork & Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/SuperNanno.git
cd SuperNanno
```

### 2. Set Up Development Environment

```bash
bash dev.sh
```

This script will:
- Create a virtual environment (`venv/`)
- Upgrade pip
- Install all dependencies from `requirements.txt`

### 3. Run the Editor

```bash
python app.py
```

---

## Development Workflow

1. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

2. **Make your changes** following the guidelines below.

3. **Test your changes** (see [Testing](#testing) section).

4. **Commit** with clear, conventional messages.

5. **Push** and open a Pull Request.

---

## Architecture Guidelines

SuperNanno follows a **clean, modular, and resilient architecture**. Please respect these principles:

- **Centralized State**: All logic should go through `AppContext`.
- **Separation of Concerns**:
  - `core/` → Business logic independent of UI
  - `services/` → High-level services (config, logging, diagnostics, etc.)
  - `handlers/` → User actions
  - `events/` → Textual event handlers (one file per event when possible)
  - `ui/` → UI components and layout
  - `search/` → Search subsystem (Strategy Pattern)
  - `states/` → Application state machine
- **Resilience**: All operations should be "best-effort". Never let logging, config, or diagnostics crash the editor.
- **Error Handling**: Use `ErrorService` (`ctx.errors.handle()`) instead of raw `try/except`.
- **Logging**: Use structured logging via `ctx.logs.info()`, `ctx.logs.error()`, etc.

**Do not** add new top-level modules without discussing first.

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_issue_service.py -v
```

- Write tests for new features when possible.
- All tests should be **independent of the Textual UI** when feasible.
- Prefer unit tests over integration tests.

---

## Pull Request Process

1. Ensure your code passes all tests.
2. Update documentation if needed (README, docstrings, etc.).
3. Make sure the PR title follows conventional commit style:
   - `feat: add XYZ`
   - `fix: correct ABC`
   - `docs: update contributing guide`
   - `refactor: improve error handling`
4. Fill out the PR template (if available).
5. Request review from maintainers.

---

## Reporting Bugs

The best way to report bugs is using the built-in **Report Service**:

- Press `Ctrl + X` while the error is visible in the status bar.
- This automatically generates a diagnostic bundle and opens a GitHub issue with all relevant information.

You can also open an issue manually on GitHub with as much detail as possible.

---

## Style Guide

- Follow **PEP 8** with a maximum line length of **100 characters**.
- Use type hints where reasonable.
- Write clear docstrings for public functions and classes.
- Prefer small, focused functions and classes.
- Keep error handling defensive and user-friendly.

---

## Questions?

Feel free to open a **Discussion** on GitHub if you have questions about the codebase, architecture, or how to implement a feature.

---

**Thank you for helping make SuperNanno better!**  
— Heitor Bardemaker A. Bisneto