# Host reboot and container recovery contracts

## Linux VPS (authoritative)

Host lifecycle owns only the unified container unit:

- Unit: `deployment/insight-unified-container.service`
- Image: immutable `${INSIGHT_UNIFIED_IMAGE}` (`name@sha256:<64hex>`)
- Publish: `127.0.0.1:8080:8080` only (module ports stay inside the supervisor)
- Restart policy: `Restart=on-failure` with `RestartSec=5`
- Data: named Docker volumes per module under `/var/lib/insight/<module>`
- Secrets: read-only `/run/secrets` from `/etc/insight/unified/secrets`
- Stop budget: `TimeoutStopSec=60` / `docker stop --time 45` for graceful SIGTERM

After host reboot, systemd brings the unit back; volumes retain SQLite files.
Module processes are not host units — `deployment/supervisor.py` remains PID
tree manager inside the container (tini as PID 1).

Standalone Treatment Plan unit (when not on unified image):
`Modules/Treatment-Plan/deployment/treatment-plan-container.service` follows the
same digest + loopback + volume pattern on port `127.0.0.1:8000`.

## Verification without real reboot

Realtime host reboot is not exercised in CI. Contract tests assert:

- restart policy and volume mounts in the systemd unit
- compose loopback bind and named volumes
- offline `python scripts/verify_unified_deployment.py topology`
- optional live path: `container --recovery` (docker kill/start) when Docker exists

## Windows Docker Desktop

No systemd. Recovery is operator-driven: restart Docker Desktop, then recreate
the compose service with the same digest and volume names. See
`deployment/WINDOWS_DOCKER_DESKTOP.md`.
