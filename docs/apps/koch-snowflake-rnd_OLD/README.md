# Koch Snowflake with Randomness

A Pyodide/PyScript mini-app for exploring how bounded randomness roughens the classical Koch snowflake while preserving recursive structure.

## Files

```text
shared/book.css
apps/koch-snowflake-rnd/index.html
apps/koch-snowflake-rnd/style.css
apps/koch-snowflake-rnd/koch_core.py
apps/koch-snowflake-rnd/app.py
```

## Run locally

Because browser module loading and PyScript behave better from a web server than from `file://`, run a tiny local server from the project root:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/apps/koch-snowflake-rnd/
```

## GitHub Pages

Copy the folders into your GitHub Pages repo. The app expects `../../shared/book.css` relative to `apps/koch-snowflake-rnd/index.html`, matching the companion-app structure.
