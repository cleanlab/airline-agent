# Development

## Tools

This project uses [Hatch] ([installation instructions][hatch-install]). Hatch automatically manages dependencies and runs testing, type checking, and other operations in isolated [environments][hatch-environments].

This project also uses [EditorConfig].

[Hatch]: https://hatch.pypa.io/
[hatch-install]: https://hatch.pypa.io/latest/install/
[hatch-environments]: https://hatch.pypa.io/latest/environment/
[EditorConfig]: https://editorconfig.org/

## Testing

You can run the tests on your local machine with:

```bash
hatch test
```

Some tests check basic functionality or the testing infrastructure itself; these are located in <tests/func>.

The majority of the tests are located in <tests/stable> and test stability. These tests are annotated with the `main` or `additional` [marks][pytest-mark], for tests in the "main" part of the readme vs. "additional" tests, respectively. You can run the relevant subset of the tests by using the `-m` flag, for example, `hatch test -v tests/stable -m main`.

[pytest-mark]: https://docs.pytest.org/en/stable/example/markers.html

## Type checking

You can run the [mypy static type checker][mypy] with:

```bash
hatch run types:check
```

[mypy]: https://mypy-lang.org/

## Formatting and linting

You can run the [Ruff][ruff] formatter and linter with:

```bash
hatch fmt
```

This will automatically make [safe fixes][fix-safety] to your code. If you want to only check your files without making modifications, run `hatch fmt --check`.

[ruff]: https://github.com/astral-sh/ruff
[fix-safety]: https://docs.astral.sh/ruff/linter/#fix-safety

## Red teaming

This repository includes a "red teaming agent" that you can use to assist you in finding issues with the airline support agent. You can run the red-teaming agent backend with:

```bash
hatch run backend-server --mode red-teaming
```

This backend is compatible with the frontend for the airline support agent. The red teaming agent ignores the "Cleanlab Disabled/Enabled" setting.

## Continuous integration

Testing, type checking, and formatting/linting is [checked in CI][ci]. The stability of the README examples is also [checked in CI][stability-ci].

[ci]: .github/workflows/ci.yml
[stability-ci]: .github/workflows/stable.yml
