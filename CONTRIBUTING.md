# Contributing Guide

Thank you for your interest in contributing to **ecommerce-drf-api**!

Please read and follow these guidelines before starting any work. They help us maintain a clean, secure, and maintainable codebase.

---

## 1. General Rules

- Never commit directly to `main` or `develop`.
- Create a separate branch for every feature, bug fix, refactor, or maintenance task.
- All changes must be submitted through a Pull Request (PR).
- Every PR must be reviewed and approved by the project lead before merging.
- Only the project lead is authorized to merge PRs into `main` or `develop`.
- Do not merge your own PR unless explicitly authorized by the project lead.
- Keep your branch focused on a single task whenever possible.
- If you cannot complete a task or expect a delay, inform the team as early as possible.
- Do not include unrelated changes in your PR.

## 2. Branch Naming Convention

Use the following naming conventions:

| Type | Format | Example |
|---|---|---|
| New feature | `feature/short-name` | `feature/cart-api` |
| Bug fix | `fix/short-name` | `fix/phone-normalization` |
| Refactoring | `refactor/short-name` | `refactor/product-serializer` |
| Maintenance | `chore/short-name` | `chore/add-drf-spectacular` |
| Documentation | `docs/short-name` | `docs/update-contributing-guide` |
| Tests | `test/short-name` | `test/cart-api-tests` |

**Rules:**
- Use lowercase English letters.
- Separate words with hyphens (`-`).
- Keep branch names short and descriptive.
- Do not use spaces or personal names in branch names.

## 3. Commit Message Convention

All commit messages must follow the Conventional Commits format:

```text
type(scope): short description
```

The `scope` is optional when it is not necessary.

### Allowed Types

| Type | Purpose | Example |
|---|---|---|
| `feat` | Add a new feature | `feat(cart): add cart API` |
| `fix` | Fix a bug | `fix(accounts): normalize phone numbers` |
| `refactor` | Improve code structure without changing behavior | `refactor(catalog): simplify product serializer` |
| `docs` | Update documentation | `docs: update API documentation` |
| `chore` | Maintenance and configuration changes | `chore(deps): add drf-spectacular` |
| `test` | Add or update tests | `test(cart): add cart API tests` |
| `style` | Formatting changes without logic changes | `style: fix import ordering` |

### Good Examples

```text
feat(orders): create orders from cart
fix(accounts): resolve phone number uniqueness issue
refactor(catalog): improve product filtering
chore: update requirements.txt
test(addresses): add address CRUD tests
docs: update contributing guide
```

### Invalid Examples

```text
task8
fix bug
update
api ali afshari
changes
WIP
```

**Rules:**
- Write commit messages in English.
- Use the imperative mood in the description.
- Keep the subject concise and descriptive.
- Do not end the subject with a period.
- Do not include unrelated changes in a commit.

## 4. Recommended Git Workflow

### Step 1: Update your local `develop` branch

```bash
git checkout develop
git pull origin develop
```

### Step 2: Create a branch for your task

Choose a name that describes your task.

```bash
git checkout -b feature/cart-api
```

### Step 3: Implement your changes

- Follow the project's coding standards.
- Keep changes focused on the assigned issue.
- Write or update tests for your changes.
- Avoid modifying unrelated files.

### Step 4: Run checks before committing

Run the checks relevant to your changes:

```bash
python manage.py check
python manage.py test
git diff --check
```

If your changes affect database models, also run:

```bash
python manage.py makemigrations --check --dry-run
```

If the project has configured linting, formatting, or CI checks, run those as well.

### Step 5: Commit your changes

```bash
git add .
git commit -m "feat(cart): add cart API"
```

Replace the example message with one that accurately describes your changes.

### Step 6: Push your branch

```bash
git push -u origin feature/cart-api
```

### Step 7: Open a Pull Request

- Open a PR on GitHub.
- Set the base branch to `develop`, unless the project lead specifies otherwise.
- Link the related issue.
- Provide a clear description of your changes.
- Request a review from the project lead.
- Wait for approval before merging.

### Step 8: After the PR is merged

Update your local `develop` branch:

```bash
git checkout develop
git pull origin develop
```

Delete the completed task branch when it is no longer needed:

```bash
git branch -d feature/cart-api
git push origin --delete feature/cart-api
```

Only delete the task branch after confirming that its changes have been merged and the branch is no longer needed.

## 5. Coding Standards

### General

- Follow Django and Django REST Framework best practices.
- Write readable, maintainable, and reusable code.
- Follow the DRY principle and avoid unnecessary duplication.
- Use clear and descriptive names for variables, functions, classes, and modules.
- Keep business logic organized and avoid unnecessarily large views or serializers.
- Remove unused imports, unnecessary comments, debugging statements, and `print()` calls before opening a PR.
- Handle errors and validation consistently.
- Do not introduce unrelated changes.

### Security and Configuration

- Never commit secrets, passwords, API keys, database credentials, or production configuration values.
- Read configuration from environment variables.
- Use a local `.env` file for development when appropriate.
- Ensure `.env` is listed in `.gitignore`.
- Provide an `.env.example` containing placeholder values when configuration documentation is needed.
- Never put real credentials in `.env.example`.
- Use secure environment configuration or a secrets manager in production.
- Never disable security protections just to make the application run.

### Testing

- Add or update tests for new features and bug fixes.
- Test important business logic, validation, permissions, authentication, and error cases where applicable.
- Do not remove or weaken existing tests just to make a change pass.
- Ensure relevant tests pass before requesting a review.
- If a test cannot be run, explain why in the PR description.

## 6. Recommended App Structure

Follow the existing project structure. The following is a general example, not a requirement to restructure existing apps:

```text
apps/
└── app_name/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── tests/
    │   ├── __init__.py
    │   └── test_example.py
    └── migrations/
```

Depending on the app's complexity, serializers, views, URLs, and tests may be organized into separate modules or packages.

- Keep each app focused on a clear responsibility.
- Follow the existing conventions of the repository.
- Avoid creating duplicate structures or moving files without a clear reason.
- Do not edit generated migration files manually unless there is a specific technical reason.

## 7. Pull Request Requirements

Before opening a PR, make sure that:

- [ ] The PR addresses an assigned task or clearly defined requirement.
- [ ] The branch follows the naming convention.
- [ ] Commit messages follow the required convention.
- [ ] The code follows the project's coding standards.
- [ ] Relevant tests have been added or updated.
- [ ] Relevant tests and checks pass.
- [ ] No secrets, credentials, or debugging statements are included.
- [ ] No unrelated files or changes are included.
- [ ] The PR description explains what changed and why.
- [ ] The related issue is linked when applicable.

### PR Title

Use a clear and descriptive title. Conventional Commit-style titles are recommended.

Examples:

```text
feat(cart): implement cart API
fix(accounts): resolve phone number validation
test(addresses): add address CRUD tests
```

### PR Description

Include the following information when relevant:

- **Summary:** What changed?
- **Reason:** Why was this change necessary?
- **Implementation:** What important technical decisions were made?
- **Testing:** Which commands were executed, and what were their results?
- **Related issue:** For example, `Closes #35`.

### Review and Merge Rules

- The project lead must approve every PR before merging.
- Required CI checks must pass before merging.
- Review feedback must be addressed before approval.
- If changes are requested, update the same branch and PR.
- Do not force-push to shared branches or rewrite shared history without coordination.
- The project lead may request changes or reject a PR that does not meet project requirements.

## 8. Database and Migration Rules

- Do not modify existing migrations that have already been shared or applied by other team members unless explicitly coordinated.
- Create migrations when model changes require them.
- Check generated migrations before committing.
- Ensure migrations are compatible with the current project state.
- Do not run destructive database operations against shared or production databases without explicit authorization.
- Coordinate changes that affect shared models or relationships with the relevant team members.

## 9. Communication and Responsibility

- Contributors are responsible for maintaining their changes until the PR is merged.
- Report blockers, unexpected behavior, and delays as early as possible.
- Ask technical questions in GitHub Issues or the team communication channel so the answers can benefit other contributors.
- Do not silently abandon assigned tasks.
- If a merged change is reverted because of a defect, cooperate with the team to investigate and resolve the issue.
- Coordinate changes that affect other contributors' work before making them.

## 10. Final Notes

These guidelines are intended to keep `ecommerce-drf-api` consistent, secure, testable, and maintainable.

When a project-specific instruction conflicts with this guide, ask the project lead for clarification before proceeding.

Thank you for contributing to `ecommerce-drf-api`!
