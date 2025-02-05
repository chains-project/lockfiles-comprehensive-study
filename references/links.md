# Lockfiles

## NPM
- [install](https://github.com/npm/cli/blob/latest/lib/commands/install.js)
- [ci](https://github.com/npm/cli/blob/latest/lib/commands/ci.js)
- [dependency tree resolution](https://github.com/npm/cli/tree/latest/workspaces/arborist)
- [lockfile validation](https://github.com/npm/cli/blob/latest/lib/utils/validate-lockfile.js)

## Cargo
- [install](https://github.com/rust-lang/cargo/blob/master/src/bin/cargo/commands/install.rs)
- [lockfile related actions](https://github.com/rust-lang/cargo/blob/master/src/cargo/ops/lockfile.rs)

## PNPM
- [module](https://github.com/pnpm/pnpm/tree/main/lockfile)
- [install action](https://github.com/pnpm/pnpm/tree/main/pkg-manager/core/src/install)

## Poetry
- [installer](https://github.com/python-poetry/poetry/blob/main/src/poetry/installation/installer.py)
- [Locker](https://github.com/python-poetry/poetry/blob/main/src/poetry/packages/locker.py)

## Pipenv
- [command.py](https://github.com/pypa/pipenv/blob/main/pipenv/cli/command.py)
- [install.py](https://github.com/pypa/pipenv/blob/main/pipenv/routines/install.py)
- [locking.py](https://github.com/pypa/pipenv/blob/main/pipenv/utils/locking.py)
- [lock.py](https://github.com/pypa/pipenv/blob/main/pipenv/routines/lock.py)

## Gradle
- [org.gradle.internal.locking](https://github.com/gradle/gradle/tree/master/platforms/software/dependency-management/src/main/java/org/gradle/internal/locking)
- [org.gradle.api.internal.artifacts.dsl.dependencies](https://github.com/gradle/gradle/tree/master/platforms/software/dependency-management/src/main/java/org/gradle/api/internal/artifacts/dsl/dependencies)

## Documentation
- [NPM](https://docs.npmjs.com/cli/v11/commands)
- [PNPM](https://pnpm.io/cli/install)
- [Cargo](https://doc.rust-lang.org/cargo/commands/cargo-build.html)
- [Cargo (TOML vs Lock)](https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html)
- [Gradle](https://docs.gradle.org/current/userguide/dependency_locking.html)
- [Poetry](https://python-poetry.org/docs/basic-usage/#installing-dependencies)
- [Pipenv](https://pipenv.pypa.io/en/latest/commands.html)