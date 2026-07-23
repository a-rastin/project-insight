# Windows Docker Desktop constraints (unified runtime)

Use this note with `deployment/compose.unified.yaml`, `deployment/verify.ps1`, and
`deployment/test.ps1`. Generally target native Ubuntu CI for gate authority;
Windows Desktop is a developer convenience path only.

## Required host shape

- Docker Desktop with the Linux engine (WSL2 backend recommended).
- Compose file published ports must stay loopback-only:
  `127.0.0.1:8080:8080`. Do not publish module ports `8101-8109`.
- Immutable image reference only:

  ```powershell
  $env:INSIGHT_UNIFIED_IMAGE = 'registry.example/insight-unified@sha256:<64-hex>'
  ```

  Mutable tags (`:latest`, `:0.1.0`) are rejected by verification tools.

## Path mounts

- Prefer Docker named volumes from compose (`authentication-data`, …). Avoid
  binding Windows drive letters into clinical DB paths when possible.
- If a secrets directory is required:

  ```powershell
  $env:INSIGHT_SECRETS_DIR = (Resolve-Path .\deployment\secrets-empty).Path
  ```

  Mount is read-only at `/run/secrets`.
- WSL path translation: when invoking compose from PowerShell against a repo on
  a Windows drive, run from the same filesystem the engine can see, or clone
  under `\\wsl$\...` / a WSL home path to avoid flipped path separators and
  ACL surprises on SQLite files.

## Compose / Desktop specifics

- File sharing must include the repo root if bind mounts are added later.
- `read_only: true` plus tmpfs entries for `/tmp`, `/run`, nginx cache/log are
  required; Desktop must allow tmpfs.
- Resource caps in systemd/unit form do not apply on Desktop; still keep the
  image non-root and read-only for parity with Linux hosts.
- Host reboot recovery on Linux is modeled by
  `deployment/insight-unified-container.service` (`Restart=on-failure` and
  persistent named volumes). On Windows Desktop there is no systemd unit:
  restart Docker Desktop, then `docker compose -f deployment/compose.unified.yaml up -d`
  with the same digest and volume names.

## Verification entrypoints

```powershell
# Offline contracts (no container required)
.\deployment\test.ps1

# Live gateway smoke when the unified stack is already up on loopback
python .\scripts\verify_unified_deployment.py unified --base-url http://127.0.0.1:8080
```

Trivy is the CI/primary scanner. Docker Scout may be used interactively on a
developer machine only when Trivy is missing; CI never requires Scout.
