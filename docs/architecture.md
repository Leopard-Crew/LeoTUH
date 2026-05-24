# LeoTUH Architecture Baseline

LeoTUH is a Leopard/PPC translation-unit preparation helper.

LeoTUH is not a build system, compiler wrapper, IDE, package manager, or
replacement for make, xcodebuild, Xcode, gcc, or project-local build rules.

LeoTUH may scan sources, classify translation-unit safety, plan temporary source
aggregation groups, and emit disposable generated files below `build/leotuh/`.

LeoTUH must not compile, link, edit source files, edit vendored code, or become
the authority for a project's build.

Deleting `build/leotuh/` must restore the project to its normal build behavior.

## Operating Model

LeoTUH has four conceptual stages:

1. `scan` — collect source facts.
2. `plan` — classify and group safe candidates.
3. `emit` — write temporary aggregation files.
4. `report` — explain decisions and measurements.

There is intentionally no `build` stage.

## Authority Boundary

The project-local build remains sovereign.

LeoTUH may prepare advisory files. The existing project decides whether and how
to consume them.

## Generated Files

Generated files must be disposable and must live below:

```text
build/leotuh/
````

LeoTUH must never generate files inside `vendor/`.

## Release Policy

LeoTUH is for local development and measurement first.

Release usage is prohibited until explicitly justified by measurement and  
approved per project.

