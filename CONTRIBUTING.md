# Contributing to QueryGuard CLI

First off, thanks for taking the time to contribute! 🎉

We love pull requests from everyone. By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## 🛠️ Development Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging. You will need Python 3.12+ installed.

### 1. Fork and Clone
Fork the repository on GitHub, then clone your fork locally:

```bash
git clone [https://github.com/mark-de-haan/query-guard-cli.git](https://github.com/mark-de-haan/query-guard-cli.git)
cd queryguard-cli
```

### 2. Install Dependencies
Install the project dependencies (including development tools) using Poetry:

```bash
# This creates a virtual environment and installs everything
poetry install
```

### 3. Verify Installation
Ensure the CLI is working in your environment:

```bash
poetry run bqg --help
```

## 💻 Making Changes
1. Create a Branch
Always work on a new branch for your specific feature or fix:

```bash
git checkout -b feat/my-amazing-feature
# or
git checkout -b fix/annoying-bug
```

2. Coding Standards
  * Type Hinting: We use strict type hinting (Python 3.12+ style). Please ensure all new functions have type hints.
  * Formatting: We use Black.

```bash
# Run formatter before committing
poetry run black .
```

3. Running Locally
To test your changes against a real BigQuery project, use poetry run to execute the CLI script:

```bash
# Example: Running a global scan locally
poetry run bqg scan --project <YOUR_TEST_PROJECT> --global
```

## 🚀 Submitting a Pull Request
1. **Push your branch** to your fork:
  ```bash
  git push origin feat/my-amazing-feature
  ```

2. **Open a Pull Request** on the main repository.
3. **Descriptive Title:** Use a clear title (e.g., "Add JSON output format" or "Fix crash on empty regions").
4. **Description:** Briefly explain what you changed and why.

### PR Checklist
[ ] My code follows the code style of this project (Black).  
[ ] I have tested the changes locally.  
[ ] I have updated the documentation (if applicable).  

## 🐛 Reporting Bugs
If you find a bug, please create an issue on GitHub with:

1. **Command Run:** The exact command you ran (e.g., bqg scan ...).
2. **Error Output:** The full traceback or error message.
3. **Environment:** Your OS and Python version.

Thanks for hacking on QueryGuard! 🛡️
