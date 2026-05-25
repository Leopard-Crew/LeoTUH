# Ultimate++ BLITZ Extraction Notes

LeoTUH does not port Ultimate++ BLITZ.

LeoTUH extracts only the technical safety model behind BLITZ-style translation
unit aggregation.

## Accepted Technical Ideas

- Temporary source aggregation files.
- Stable-file heuristic.
- Explicit approve/prohibit markers.
- Header guard checks.
- Conservative include scanning.
- Local macro cleanup after included source files.
- Per-file aggregation index macro.
- Fallback to normal compilation for unsafe files.
- Debug/local iteration focus.

## Rejected Architecture

- TheIDE integration.
- Ultimate++ package model.
- Ultimate++ build method model.
- `umk` command model.
- Build-system ownership.
- Automatic compiler invocation.
- Release BLITZ as a default mode.
- Source tree rewriting.
- Vendored code modification.

## LeoTUH Interpretation

Ultimate++ BLITZ is useful because it demonstrates that source aggregation is
not just concatenation. The valuable part is the safety envelope around
aggregation.

LeoTUH must therefore begin as a scanner and reporter before becoming an
emitter.

## Naming

Ultimate++ uses BLITZ terminology.

LeoTUH must not import BLITZ naming into its public interface.

Preferred LeoTUH markers:

```cpp
// LEO_TUH_APPROVE
// LEO_TUH_PROHIBIT
````

Preferred generated macros:

```cpp
#define LEO_TUH_ACTIVE__ 1
#define LEO_TUH_GROUP__  1
#define LEO_TUH_INDEX__  1
```

## Stable-File Heuristic

Recently modified files must not be aggregated by default.

The first default stability window is:

```text
3600 seconds
```

This prevents actively edited files from forcing rebuilds of a larger generated  
translation unit.

## Safety Policy

`LEO_TUH_PROHIBIT` is absolute.

`LEO_TUH_APPROVE` is an override, but it must remain visible in reports.

Manual approval must never hide risk.

## Core Rule

LeoTUH may make translation-unit risk visible and optionally exploitable.

LeoTUH must not make the build clever behind the user's back.  

