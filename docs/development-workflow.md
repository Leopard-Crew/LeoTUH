# LeoTUH Development Workflow

LeoTUH is developed against a real Mac OS X 10.5.8 PowerPC system.

## Host Roles

NozzlePoint is the orchestration host.

The iMac G5 is the native execution and validation host.

## Paths

On NozzlePoint, the iMac project volume is mounted at:

```text
/mnt/imac_admin/Desktop/Projekte/LeoTUH
````

On the iMac G5, the same working tree is available at:

```text
/Users/admin/Desktop/Projekte/LeoTUH
```

These paths refer to the same working tree.

## Git Rule

Git is orchestrated exclusively from NozzlePoint.

The iMac G5 may run tools, smoke tests, build probes, and measurements, but it  
must not be used for commits, tags, pushes, pulls, or branch operations during  
normal LeoTUH development.

This avoids concurrent access problems in the shared `.git` directory.

## Native Validation

Smoke tests should be run on both hosts when practical:

```sh
tools/run_scan_smoke.sh
```

A test passing on NozzlePoint proves tooling portability.

A test passing on the iMac G5 proves Leopard/PPC viability.

## Current Baselines

```text
v0.1.0-scope-baseline
  Scope and architecture baseline.

v0.2.0-scan-smoke-baseline
  First scan-only helper and smoke-test baseline.
```

