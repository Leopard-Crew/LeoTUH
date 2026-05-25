# LeooRexx Scan Probe 001: StringClass.cpp

## Target

```text
/mnt/imac_admin/Desktop/Projekte/LeooRexx/src/oorexx-3.2.0-leopard/kernel/classes/StringClass.cpp
````

Equivalent native Leopard path:

```text
/Users/admin/Desktop/Projekte/LeooRexx/src/oorexx-3.2.0-leopard/kernel/classes/StringClass.cpp
```

## Purpose

Validate whether LeoTUH can scan a real LeooRexx source file and resolve direct  
local headers through explicit include directories.

## Include Directories Used

```text
src/oorexx-3.2.0-leopard/kernel
src/oorexx-3.2.0-leopard/kernel/classes
src/oorexx-3.2.0-leopard/kernel/runtime
src/oorexx-3.2.0-leopard/kernel/expression
src/oorexx-3.2.0-leopard/kernel/instructions
src/oorexx-3.2.0-leopard/kernel/parser
src/oorexx-3.2.0-leopard/api
```

## Result

LeoTUH resolved the relevant local headers successfully.

All directly scanned local headers for this probe were detected as guarded via  
classic `#ifndef` / `#define` include guards.

## Important Finding

The source file reports a local define:

```text
this
```

This is a potential translation-unit aggregation risk.

LeoTUH should later classify such defines as risky local defines. This should  
not automatically rewrite or modify the source file. The scanner should only  
report the risk.

## Interpretation

The probe confirms that LeooRexx is not immediately blocked at the direct-header  
guard level when proper include directories are supplied.

The next LeoTUH scanner improvement should be risky local-define reporting.  

