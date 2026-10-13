# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.4.x   | ✅        |
| 0.3.x   | ⚠️ security fixes only |
| < 0.3   | ❌        |

## Reporting a vulnerability

Email `security@ai-workout-plan-generator.dev` with a description, a
reproducer, and the affected version. We aim to acknowledge within 72 hours
and ship a patch within 14 days for high-severity issues.

Do not open a public issue for anything involving remote code execution,
path traversal in the export handler, or the local inference socket.

## Threat model

This is a desktop tool. The relevant surfaces are:

1. **Local inference socket** — `services/inference.py` binds to `127.0.0.1`
   only. If you find it binding to `0.0.0.0`, that is a critical bug.
2. **Export paths** — `handlers/export.py` writes user-chosen paths. It must
   resolve and re-check the path after canonicalization. Path traversal here
   is in scope.
3. **Remote backend** — disabled by default. When enabled, it sends only the
   intake form, never the user's history, unless the user opts in per-field.
4. **Model files** — we load `.onnx` and `.pt` from `models/checkpoints/`.
   Arbitrary pickle loading is not in scope for fixes; we don't use `pickle`.

## Out of scope

- Physical injury from following a generated plan. This is a planning tool,
  not medical advice. Users must consult a professional before starting.
- Denial of service against the local socket by the same user running the app.