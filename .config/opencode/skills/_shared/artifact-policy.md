# Durable Artifact Output

Apply this policy whenever the workflow writes a durable document.

1. Determine the active branch only through a capability declared by the project or current environment. Do not assume a VCS or a remembered command. If the branch cannot be determined reliably, use `global`.
2. Convert the scope to one safe path component: retain letters, digits, `.`, `_`, and `-`; replace every other run with `-`; trim leading and trailing separators. Use `global` if the result is empty.
3. Build the destination as `~/.agents/docs/<scope>/YYYY-MM-DD-HHMMSS-<skill>-<descriptive-slug>.md`.
4. Create the scope directory through the available filesystem capability. If the destination already exists, choose a new timestamp or append a numeric suffix. Never overwrite an existing artifact.
5. Write the document there even when an upstream workflow suggests the project tree or an operating-system temporary directory.
6. Redact credentials, tokens, private keys, and personal data that are not essential to the document.
7. Report the absolute artifact path when the write succeeds. If the write fails, preserve the content in the response and report the failure accurately.
