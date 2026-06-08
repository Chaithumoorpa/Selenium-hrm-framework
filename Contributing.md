# Contributing Guide — Enterprise Selenium HRM Framework

## Git Branching Strategy

We follow **GitFlow** adapted for SDET teams:

```
main          ← Production-ready, protected, requires PR + review
  │
  ├── develop ← Integration branch, all features merge here first
  │     │
  │     ├── feature/TC-XXX-short-description   ← New test/feature
  │     ├── fix/TC-XXX-flaky-login-test        ← Bug/flaky fix
  │     ├── refactor/page-locator-separation   ← Non-test changes
  │     └── chore/update-dependencies          ← Deps, config updates
  │
  └── release/v1.2.0   ← Release candidate (from develop)
        │
        └── hotfix/critical-smoke-failure      ← Urgent prod fix
```

### Branch Naming Convention

| Type | Format | Example |
|------|--------|---------|
| Feature | `feature/TC-XXX-description` | `feature/TC-LGN-011-oauth-login` |
| Bug Fix | `fix/TC-XXX-description` | `fix/TC-EMP-003-search-flaky` |
| Refactor | `refactor/description` | `refactor/pom-base-page-split` |
| Chore | `chore/description` | `chore/upgrade-selenium-4.23` |
| Release | `release/vX.Y.Z` | `release/v2.1.0` |
| Hotfix | `hotfix/description` | `hotfix/smoke-failure-login` |

---

## Pull Request Strategy

### Before Opening a PR

```bash
# 1. Sync with latest develop
git fetch origin
git rebase origin/develop

# 2. Run quality checks locally
make quality       # format + lint + typecheck

# 3. Run affected test suite
make smoke         # At minimum

# 4. Verify Docker build
make docker-build

# 5. Collect test report
make report
```

### PR Requirements (enforced by branch protection rules)

- [ ] All CI checks pass (lint + smoke)
- [ ] PR description includes test evidence (Allure screenshot or log)
- [ ] At least 1 reviewer approved
- [ ] Branch is up-to-date with `develop`
- [ ] No new `@pytest.mark.flaky` without Jira ticket reference

### PR Description Template

```markdown
## Summary
<!-- What does this PR add/change/fix? -->

## Test Cases Added / Modified
| TC ID | Description | Status |
|-------|-------------|--------|
| TC-LGN-011 | OAuth2 login flow | ✅ New |

## Test Evidence
<!-- Attach Allure screenshot or paste test output -->

## Checklist
- [ ] Tests added/updated
- [ ] Locators reviewed for stability
- [ ] No hardcoded credentials
- [ ] Allure annotations added (@story, @title, @severity)
- [ ] New markers added to pytest.ini

## Breaking Changes
<!-- List any breaking changes or None -->
```

---

## Code Review Checklist

### For Reviewers — Must Check

#### Test Quality
- [ ] **Assertions are meaningful** — not just `assert True`
- [ ] **Test has a clear Given/When/Then** (even if not BDD)
- [ ] **Negative test cases included** for every positive flow
- [ ] **Allure decorators present** (`@allure.title`, `@allure.severity`, `@allure.story`)
- [ ] **pytest.mark decorators present** (`@smoke`, `@regression`, module marker)

#### Page Objects
- [ ] **Locators live in `locators/`** — not inside page classes
- [ ] **Page methods return `self`** for method chaining where appropriate
- [ ] **`BasePage` methods used** — no raw `driver.find_element()` in page classes
- [ ] **`@allure.step`** decorates every meaningful page action

#### Code Quality
- [ ] **No hardcoded URLs** — use `config.base_url`
- [ ] **No hardcoded credentials** — use `config.admin_username`
- [ ] **No `time.sleep()`** without a comment explaining why (use explicit waits instead)
- [ ] **Logger used** instead of `print()` for debug output
- [ ] **No commented-out code** in PRs

#### Reliability
- [ ] **Flaky-proof locators** — prefer IDs/data-testid over text-based XPaths where possible
- [ ] **Retry decorator** applied to click/type actions that can throw `StaleElementReferenceException`
- [ ] **Screenshot on failure** — no bare assertions without context

---

## Coding Standards

### Python Style
- **Black** for formatting: `black . --line-length=120`
- **isort** for imports: `isort .`
- **flake8** for linting: `flake8 . --max-line-length=120`
- **Type hints** required for all public methods

### Naming Conventions

| Artifact | Convention | Example |
|----------|-----------|---------|
| Page class | `PascalCase + Page` | `LoginPage` |
| Locator class | `PascalCase + Locators` | `LoginLocators` |
| Test class | `Test + Module` | `TestLogin` |
| Test method | `test_action_scenario` | `test_login_invalid_credentials` |
| Fixture | `snake_case` | `authenticated_driver` |
| Config key | `snake_case.nested` | `app.base_url` |

### Test ID Convention
```
TC-[MODULE]-[NUMBER]: TC-LGN-001, TC-EMP-003, TC-LVE-007
```

---

## Release Strategy

### Versioning: Semantic Versioning (semver)
- `MAJOR.MINOR.PATCH` — e.g., `v2.1.3`
- **MAJOR**: Breaking framework changes (config schema, fixture API)
- **MINOR**: New module test coverage added
- **PATCH**: Bug fixes, locator updates, flaky test fixes

### Release Checklist
- [ ] All regression tests pass on `staging` environment
- [ ] Allure report reviewed — no new failures vs. previous release
- [ ] `requirements.txt` pinned versions reviewed
- [ ] CHANGELOG.md updated
- [ ] Docker image tagged with version
- [ ] K8s configmap version label updated

---

## Reporting a Bug in the Framework

Open a GitHub Issue with:
1. **TC ID** (if test-related)
2. **Reproduction steps**
3. **Expected vs. Actual behavior**
4. **Allure report link or screenshot**
5. **Environment**: OS, browser, Python version
