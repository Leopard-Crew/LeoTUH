# LeoTUH Scope Files

## Purpose

LeoTUH scope files describe a reproducible scan scope for a target project.

They are used by `tools/leotuh_scan_tree.py` through:

```text
--scope-file PATH
````

Scope files do not build, modify, classify, or approve source files. They only  
provide scan input.

## Path Rule

All paths inside a scope file are interpreted relative to the current working  
directory from which `leotuh_scan_tree.py` is executed.

For project scans, run LeoTUH from the target project root.

Example:

```sh
cd /path/to/TargetProject

python3 ../LeoTUH/tools/leotuh_scan_tree.py \
  --scope-file ../LeoTUH/examples/leorexx.leotuh-scope \
  --stable-age 0
```

## Format

The file format is line-oriented.

Empty lines are ignored.

Lines beginning with `#` are comments.

All non-comment lines use:

```text
key=value
```

Unknown keys are errors.

Empty values are errors.

## Supported Keys

### root

Defines the source-tree root to scan.

```text
root=src/oorexx-3.2.0-leopard
```

Only one `root` entry should be used.

If no `root` entry is present, the command-line default is used.

### include-dir

Adds an include directory used to resolve direct local headers.

```text
include-dir=src/oorexx-3.2.0-leopard/kernel/runtime
```

This key may appear multiple times.

### exclude-path

Excludes a root-relative path from scanning.

```text
exclude-path=platform/windows
```

This key may appear multiple times.

The exclusion applies to the exact path and everything below it.

### prune

Prunes directories by basename.

```text
prune=build-work
```

This key may appear multiple times.

Prefer `exclude-path` for reproducible project-specific scope rules.

Use `prune` only for generic directory names.

## Precedence

Scope-file entries and command-line entries are combined.

Command-line entries do not erase scope-file entries.

This allows a reusable base scope plus temporary command-line additions.

## Non-Goals

Scope files are not build descriptions.

They do not replace Makefiles, Xcode projects, or compiler flags.

They do not approve files for aggregation.

They do not decide target-project cleanup policy.

## Current Example

See:

```text
examples/leorexx.leotuh-scope
```

This example is a LeoTUH scan example for LeooRexx. It is not a LeooRexx source  
cleanup decision.  

