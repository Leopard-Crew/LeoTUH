# LeooRexx Tree Scan Probe 001

## Purpose

Validate LeoTUH's tree-scan reporter against a real Leopard/PPC target tree.

This probe is a LeoTUH scanner validation only. It does not decide LeooRexx
source-tree cleanup policy and does not imply source removal.

## Target

```text
/mnt/imac_admin/Desktop/Projekte/LeooRexx/src/oorexx-3.2.0-leopard
````

Equivalent native Leopard path:

```text
/Users/admin/Desktop/Projekte/LeooRexx/src/oorexx-3.2.0-leopard
```

## Tool Version Context

The relevant LeoTUH baseline before this probe:

```text
v0.2.1-header-risk-scan
```

Tree scan reporter commit:

```text
d03d8a5 Add tree scan reporter
```

Repository hygiene commit after the probe:

```text
f90eeed Ignore LeoTUH build artifacts
```

## Include Directories

```text
src/oorexx-3.2.0-leopard/kernel
src/oorexx-3.2.0-leopard/kernel/classes
src/oorexx-3.2.0-leopard/kernel/runtime
src/oorexx-3.2.0-leopard/kernel/expression
src/oorexx-3.2.0-leopard/kernel/instructions
src/oorexx-3.2.0-leopard/kernel/parser
src/oorexx-3.2.0-leopard/api
```

## Broad Scan Result

The initial broad scan included non-Leopard-relevant areas such as Windows,  
samples, and SOM-related source trees.

```text
sources_total: 231
sources_scanned: 231
sources_stable: 231
sources_recent: 0
manual_approve: 0
manual_prohibit: 0
entry_points_detected: 16
unknown_language: 0
direct_includes_total: 1979
local_headers_total: 1318
local_headers_guarded: 1097
local_headers_guarded_ifndef_define: 1097
local_headers_guarded_pragma_once: 0
local_headers_unguarded: 51
local_headers_missing: 170
local_defines_total: 1100
risky_local_defines_total: 5
```

## Pruned Scan

The second scan used these pruning options:

```text
--prune windows
--prune samples
--prune SOM
```

Result:

```text
sources_total: 158
sources_scanned: 158
sources_stable: 158
sources_recent: 0
manual_approve: 0
manual_prohibit: 0
entry_points_detected: 6
unknown_language: 0
direct_includes_total: 1506
local_headers_total: 1083
local_headers_guarded: 968
local_headers_guarded_ifndef_define: 968
local_headers_guarded_pragma_once: 0
local_headers_unguarded: 19
local_headers_missing: 96
local_defines_total: 759
risky_local_defines_total: 5
```

## Risky Local Defines

The same five risky local defines remained after pruning:

```text
kernel/classes/ArrayClass.cpp: this:cpp_keyword_macro
kernel/classes/StringClass.cpp: this:cpp_keyword_macro
kernel/classes/TableClass.cpp: this:cpp_keyword_macro
kernel/runtime/RexxBuffer.cpp: this:cpp_keyword_macro
kernel/runtime/RexxNativeActivation.cpp: this:cpp_keyword_macro
```

## Interpretation

The scan confirms that LeoTUH can produce useful aggregate facts for a real  
Leopard/PPC codebase.

The broad scan also confirms that tree scope matters. Non-target source areas  
can inflate missing-header and unguarded-header counts.

This is a LeoTUH finding only:

```text
LeoTUH must support precise source-tree scope control.
```

It is not a LeooRexx cleanup decision.

## Follow-Up

The next useful LeoTUH improvement is more precise path exclusion:

```text
--exclude-path kernel/platform/windows
--exclude-path platform/windows
--exclude-path samples
```

This is more exact than pruning by directory basename alone.  

