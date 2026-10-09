# Jane task runner. Install just: `uv tool install rust-just` (or `uvx --from rust-just just <recipe>`).
#
# No shell is involved: every recipe line is handed to scripts/dev.py (stdlib Python) together with
# the recipe arguments as separate argv items (positional-arguments). So the same commands work on
# Windows and Linux, and arguments keep their quoting: `just unit -v -k "not slow"`.

set positional-arguments := true
set shell := ["uv", "run", "--no-project", "--quiet", "python", "scripts/dev.py", "--just"]
set windows-shell := ["uv", "run", "--no-project", "--quiet", "python", "scripts/dev.py", "--just"]

# List recipes
default:
    @list

# Install/refresh the workspace environment
sync:
    @sync

# lint + types + unit + contract (+ web when web/* exists) - what CI runs; extra args go to pytest
check *args:
    @check

# ruff check, ruff format --check, contracts lint
lint:
    @lint

# Auto-fix lint issues and format code
fmt:
    @fmt

# mypy for every workspace member
types:
    @types

# Unit tests (no contract/integration/isolation marker) + offline examples/, deploy/profiles/; extra args go to pytest
unit *args:
    @unit

# Contracts lint + compat.py self-test + contract tests; extra args go to pytest
contract *args:
    @contract

# Tests of one service or library, e.g. `just test web-collector` or `just test jane-kit -k limits`
test target *args:
    @test

# Integration tests against this checkout's stack (`--project <name>` for another one)
integration *args:
    @integration

# Sandbox isolation tests (Linux only; WP-06)
isolation *args:
    @isolation

# End-to-end acceptance scenarios; stack is isolated and cleaned by the test fixture
e2e *args:
    @e2e

# Admin web checks via pnpm (when web/* exists; WP-12)
web:
    @web

# Start the dev stack with a unique compose project (`just up postgres minio` for a subset)
up *args:
    @up

# Stop the dev stack (`just down -v` also removes volumes)
down *args:
    @down

# Stack status
ps *args:
    @ps

# Stack logs (`just logs postgres`)
logs *args:
    @logs

# Print endpoints and generated credentials of the running stack
env *args:
    @env

# Create services/<name> from templates/service
new-service name:
    @new-service

# Install the git pre-commit hook (gitleaks)
hooks:
    @hooks

# Run the test site on http://127.0.0.1:8080
testsite *args:
    @testsite

# Generate a client package from an OpenAPI contract
gen-client spec out:
    @gen-client

# Contracts linter alone (`--redocly` also requires the Redocly lint via npx)
contracts-check *args:
    @contracts-check

# compat.py self-test + backward compatibility vs a git ref: `just contracts-compat [origin/main] [--oasdiff]`
contracts-compat *args:
    @contracts-compat

# Example-driven mock of one API from contracts/: `just contracts-mock handler --port 4010`
contracts-mock api *args:
    @contracts-mock

# Python client of one contract: `just contracts-gen storage services/x/src/jane_x/_generated/storage`
contracts-gen api out:
    @contracts-gen
