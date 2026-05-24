# LeooRexx First Validation Target

LeooRexx is the first intended LeoTUH validation target.

The reason is practical: LeooRexx has sufficiently long local build times to
make translation-unit aggregation measurable without being too large to study.

## Goal

Measure whether conservative translation-unit aggregation can reduce local
Leopard/PPC development build time without changing the project's build
authority.
 
## Non-Goals

- Do not modify LeooRexx source files.
- Do not edit vendored code.
- Do not replace the LeooRexx build system.
- Do not introduce LeoTUH into release builds.
- Do not assume speedup before measurement.

## Baseline Measurements

The first probe must collect:

```text
clean build time
no-op build time
one-file rebuild time
```

Suggested command pattern:

```sh
make clean
/usr/bin/time -p make 2>&1 | tee build/leotuh/baseline-clean.log

/usr/bin/time -p make 2>&1 | tee build/leotuh/baseline-noop.log
```

A later probe should measure one-file rebuild behavior after touching a single  
actively edited source file.

## First LeoTUH Probe

The first LeoTUH interaction with LeooRexx should be scan-only.

No generated translation-unit files should be consumed by the build during the  
first probe.

## Expected Findings

The first useful result is not speed.

The first useful result is a classification map:

```text
safe candidates
recent files
manual excludes
missing header guards
local macros
entry-point files
files with special compile signatures
```

## Success Criteria

LeoTUH is useful if it can produce a trustworthy explanation of which files are  
safe candidates for aggregation and why.

Build speedup is a later validation step.

