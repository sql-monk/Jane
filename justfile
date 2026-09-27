# Jane task runner. Install just: `uv tool install rust-just` (or run any recipe via `uvx --from rust-just just <recipe>`).
# Every recipe is a single call into scripts/dev.py, so the same commands work on Windows and Linux.

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]
set positional-arguments := false

dev := "uv run --no-project --quiet python scripts/dev.py"

# List recipes
default:
    @just --list --unsorted

# Install/refresh the workspace environment
sync:
    {{dev}} sync

# lint + types + unit + contract (+ web when web/* exists) - what CI runs
check *args:
    {{dev}} check {{args}}

# ruff check, ruff format --check, contracts lint
lint:
    {{dev}} lint

# Auto-fix lint issues and format code
fmt:
    {{dev}} fmt

# mypy for every workspace member
types:
    {{dev}} types

# Unit tests (everything except contract/integration/isolation markers)
unit *args:
    {{dev}} unit {{args}}

# Contracts lint + contract tests
contract *args:
    {{dev}} contract {{args}}

# Tests of one service or library, e.g. `just test web-collector` or `just test jane-kit -k limits`
test target *args:
    {{dev}} test {{target}} {{args}}

# Integration tests (need `just up`)
integration *args:
    {{dev}} integration {{args}}

# Sandbox isolation tests (Linux only; WP-06)
isolation *args:
    {{dev}} isolation {{args}}

# Admin web checks via pnpm (when web/* exists; WP-12)
web:
    {{dev}} web

# Start the dev stack with a unique compose project (`just up postgres minio` for a subset)
up *args:
    {{dev}} up {{args}}

# Stop the dev stack (`just down -v` also removes volumes)
down *args:
    {{dev}} down {{args}}

# Stack status
ps *args:
    {{dev}} ps {{args}}

# Stack logs (`just logs postgres`)
logs *args:
    {{dev}} logs {{args}}

# Print endpoints and generated credentials of the running stack
env *args:
    {{dev}} env {{args}}

# Create services/<name> from templates/service
new-service name:
    {{dev}} new-service {{name}}

# Install the git pre-commit hook (gitleaks)
hooks:
    {{dev}} hooks

# Run the test site on http://127.0.0.1:8080
testsite *args:
    {{dev}} testsite {{args}}

# Generate a client package from an OpenAPI contract
gen-client spec out:
    {{dev}} gen-client {{spec}} {{out}}
