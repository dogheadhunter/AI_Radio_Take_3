# AI Radio (minimal)

A minimal Python package for signal detection along with pytest configuration and VS Code debug setup.

## Setup

- Create a virtual environment:

  ```powershell
  python -m venv .venv
  .\.venv\Scripts\activate
  pip install -r requirements.txt
  ```

- Run tests:

  ```powershell
  .\.venv\Scripts\pytest -q
  ```


## Debugging in VS Code

Open the workspace in VS Code. Use the `Run and Debug` view and pick `Python: Debug Tests` to run pytest with the debugger attached.
