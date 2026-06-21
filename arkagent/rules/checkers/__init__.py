"""ArkTS code quality checkers.

Each checker module inspects .ets/.ts files for a specific category of issues.
Checkers are independent — callers compose them via arkagent_gate_check() or
arkagent_scan_project().

Checker categories:
    imports   — deprecated import paths, wrong module sources
    syntax    — 25 ArkTS-critical syntax error patterns
    state     — V1/V2 decorator misuse, performance anti-patterns
    security  — hardcoded secrets, missing permissions
    arch      — layer placement, module dependency direction
"""
