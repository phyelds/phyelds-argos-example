# CLAUDE.md

Examples of [phyelds](https://github.com/phyelds/phyelds) on robot swarms in ARGoS3.
Every robot runs the same aggregate program through the `phyelds_controller` of
`phyelds-argos`, a native plugin that embeds CPython and exchanges each round over the
robot's simulated radio.

- `src/phyelds_argos_examples/`: the aggregate programs, one module per example
  (`gradient`, `election`, `dispersion`, `gathering`, `flocking`); `common`: colours,
  the leader and the repulsion they share. The programs know nothing of ARGoS: they read
  the host's sensors and act through the typed objects of `phyelds.argos` (`source`,
  `heading`, `obstacle`; `velocity`, `led`, `label`), with `.sense()` and `.send(...)`,
  never strings.
- `experiments/`: one ARGoS experiment per example, and `mixed_*` ones that run the same
  programs on foot-bots, e-pucks and eye-bots together.
- `tests/test_programs.py`: every program on `phyelds.vm.device.Device`, fed the sensors
  ARGoS would give, without ARGoS. `tests/test_experiments.py` (marked `argos`) runs every
  experiment for 30 simulated seconds under `tests/native/observer.cpp`, a test-only
  observer that prints ground-truth poses; the programs never see them.
- `scripts/`: `smoke.sh` runs the experiments, `record.sh` the pictures in `docs/`.

Dependencies:

- The programs depend on `phyelds-argos` from PyPI, which ships C++ sources:
  `python -m phyelds.argos.build` compiles the plugin against the Python that runs it, so
  rebuild after changing the environment.
- `phyelds.experimental` (gathering, flocking) is a study in progress whose API may change
  in any release: pin and update it deliberately.

## Commands

```bash
uv venv --python 3.13              # Python 3.12–3.13, with development headers
source .venv/bin/activate
uv pip install -e . pytest pylint flake8   # set up the environment
python -m phyelds.argos.build --build-dir build   # the plugin; --no-gui without Qt
argos3 -c experiments/gradient.argos   # open an example, from the repository root
python -m pytest -q -m 'not argos'  # the fast tests, on Device
python -m pytest -q                # all of them, the experiments in ARGoS (needs ARGoS3, CMake)
python -m pytest tests/test_experiments.py::test_name   # a single test
python -m pylint src               # lint, as in CI
python -m flake8 src               # style, max line length 120, as in CI
scripts/record.sh gradient 10 png  # regenerate a picture (a display and FFmpeg)
```

A change is done only when `pytest` (with the experiments), `pylint` and `flake8` all
pass: CI runs exactly these, on a pinned ARGoS built from source. When a change touches
what a reader sees (an example, how to run it), also update the README and its pictures.

## Workflow: test-driven development

Every feature and every bug fix follows red → green → refactor. Do not write
production code that no failing test asks for.

1. **Understand.** Restate the requested behaviour as a short list of observable
   cases (normal case, edge cases, error cases). If a requirement is ambiguous,
   ask before writing code.
2. **Red.** Write *one* test for the next case and run it. It must fail, and fail
   for the expected reason (an assertion or a missing name, not a typo or an
   import error elsewhere). Do not write the implementation in the same step.
3. **Green.** Write the minimum code that makes that test pass. Run the whole
   suite, not only the new test.
4. **Refactor.** With the suite green, remove duplication and improve names and
   structure, in both production and test code. Run the suite after each change.
5. **Commit** (see below), then repeat from step 2 for the next case.

Rules:

- Never change or delete an existing test just to make it pass. If a test is
  wrong, say so, explain why, and fix it in its own commit.
- Never skip, `xfail` or weaken an assertion to get to green.
- For a bug, first write a test that reproduces it; the fix comes after.
- Test behaviour through the public API, not implementation details, so the
  refactor step stays free.
- A program is tested twice: on `Device` (`tests/test_programs.py`, fast) and in its
  experiment (`tests/test_experiments.py`). Reuse the helpers already there
  (`run_line`, `positions`, `polarization`) instead of building new fixtures.
- In an experiment, assert robust properties (consensus, spacing, alignment, distances
  within a tolerance), never exact trajectories: they depend on the physics engine.
- Name tests after the behaviour: `test_<unit>_<does_what>_<when>`, and lay them
  out as Arrange / Act / Assert.
- Keep tests fast and deterministic: fix random seeds, keep simulations small.

## Commits

Commit small and often: one logical change per commit, each one leaving the
suite green. A typical feature is a series of commits, e.g. a failing test plus
its implementation, then a refactor.

- Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):
  `<type>(<optional scope>): <description>`, with the types `feat`, `fix`, `test`,
  `refactor`, `docs`, `style`, `perf`, `build`, `ci`, `chore`. Nothing is released
  from this repository, but the history reads as the one of phyelds.
- Subject: imperative mood, lowercase, no trailing period, ≤ 72 characters.
- Body (when useful): wrap at 72 columns, explain *why* and what the previous
  behaviour was, not a line-by-line list of the diff. Follow the style of the
  existing history (`git log`).
- Stage files explicitly (`git add <path>`), never `git add -A` / `git add .`.
- Never use `--no-verify`; if a pre-commit hook fails, fix the cause.
- Never amend or rewrite commits that are already pushed, and do not push
  unless asked.
- **No AI attribution.** Do not add `Co-Authored-By: Claude …`, "Generated
  with Claude Code", emoji or any other reference to AI tools in commit
  messages, PR titles or PR descriptions. Commits are authored by the git user
  only.

## Python style

Follow [PEP 8](https://peps.python.org/pep-0008/),
[PEP 257](https://peps.python.org/pep-0257/) and the
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html);
pylint and flake8 enforce the mechanical part. Match the surrounding code first.

### Design and modularity

- One module, one responsibility. An aggregate program says *what* the swarm does and
  knows nothing of ARGoS; the experiment declares the robots and their devices, and the
  plugin turns sensors into the program's inputs and its outputs into motors and lights.
  Keep that direction: `phyelds_argos_examples` imports from `phyelds.argos` only the
  names of the sensors and actuators, never ARGoS or the plugin.
- Keep aggregate exchanges before local loops whose iteration counts differ among
  robots, or move the loop into a plain helper: otherwise later exchanges can take
  different alignment paths.
- Small, focused functions; a function longer than ~40 lines or with deep
  nesting is a signal to split it. Prefer early returns over nested `if`s.
- Prefer composition and plain functions over class hierarchies; use
  `dataclass` for data carriers.
- Keep side effects at the edges and pure logic in the middle, so it is easy
  to test.
- No mutable module-level state; if it is unavoidable, make it private
  (`_name`) and expose it through functions.
- Do not duplicate: look for an existing helper, here or in phyelds, before writing a
  new one.
- Do not add a dependency without asking.

### Code

- Type-annotate every public function, method and attribute. Use modern
  syntax: `list[int]`, `X | None`, `collections.abc` abstract types for
  parameters (`Sequence`, `Mapping`, `Callable`).
- Naming: `lower_with_under` for modules, functions and variables, `CapWords`
  for classes, `CAPS_WITH_UNDER` for constants, a leading `_` for internals.
  Descriptive names, no type in the name, no single letters outside short
  loops or maths. Do not shadow builtins (`max`, `min`, `id`, `list`, …).
- Physical quantities in SI units (metres, seconds, radians), and say so in the name or
  the docstring. Robot IDs in an experiment end in a unique integer, across all robot
  types (`base_num` on a `distribute`).
- Imports: absolute (`from phyelds.calculus import aggregate`), grouped as
  standard library / third party / local, no wildcard imports.
- Never use mutable default arguments; default to `None` and build the value
  inside.
- Exceptions: raise specific built-in ones (`ValueError`, `TypeError`) or a
  custom one ending in `Error`; no bare `except:`, no broad `except Exception`
  unless re-raising; keep `try` blocks small. Do not use `assert` for runtime
  checks in library code (it is fine in tests).
- Comprehensions only when they stay simple; otherwise use a loop.
- Use f-strings, `pathlib`, context managers (`with`) for resources, and
  `logging` instead of `print` in library code.
- Executable scripts put their logic in `main()` behind
  `if __name__ == "__main__":`.

### Docstrings and comments

- Every public module, class and function has a docstring in Google style: a
  one-line summary ending with a period, then `Args:`, `Returns:` (or
  `Yields:`) and `Raises:` when relevant. Describe behaviour and contract, not
  implementation.
- Comments explain *why*, not *what*. Do not leave commented-out code, TODOs
  without context, or comments describing the change you just made.
- Update the README or docstrings when what an example shows changes.
