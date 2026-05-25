#!/bin/sh
#
# LeoTUH scan smoke test.
#
# This script intentionally uses plain /bin/sh features for Leopard compatibility.

if [ -z "$PYTHON" ]; then
    if command -v python >/dev/null 2>&1; then
        PYTHON=python
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON=python3
    else
        echo "FAIL: no Python interpreter found"
        exit 1
    fi
fi

ROOT=`dirname "$0"`/..
OUT="$ROOT/build/leotuh/scan-smoke.out"

mkdir -p "$ROOT/build/leotuh"

fail()
{
    echo "FAIL: $1"
    echo "---- scanner output ----"
    cat "$OUT"
    exit 1
}

cd "$ROOT" || exit 1

$PYTHON tools/leotuh_scan.py --stable-age 0 testdata/simple/sample.cpp > "$OUT" || exit 1

grep -q "local: sample.h" "$OUT" || fail "sample.h local include was not detected"
grep -q "system: stdio.h" "$OUT" || fail "stdio.h system include was not detected"
grep -q "sample.h: guarded=yes guard_style=ifndef_define" "$OUT" || fail "sample.h include guard was not detected"
grep -q "LOCAL_FLAG" "$OUT" || fail "LOCAL_FLAG define was not detected"

$PYTHON tools/leotuh_scan.py --stable-age 0 testdata/scan_noise/noise.cpp > "$OUT" || exit 1

grep -q "local: real.h" "$OUT" || fail "real.h local include was not detected"
grep -q "real.h: guarded=yes guard_style=ifndef_define" "$OUT" || fail "real.h include guard was not detected"
grep -q "NOISE_FLAG" "$OUT" || fail "NOISE_FLAG define was not detected"

if grep -q "hidden_block_comment.h" "$OUT"; then
    fail "block-comment include was incorrectly detected"
fi

if grep -q "hidden_line_comment.h" "$OUT"; then
    fail "line-comment include was incorrectly detected"
fi

if grep -q "hidden_string.h" "$OUT"; then
    fail "string literal include was incorrectly detected"
fi

$PYTHON tools/leotuh_scan.py --stable-age 0 testdata/scan_noise/unguarded.cpp > "$OUT" || exit 1

grep -q "local: unguarded.h" "$OUT" || fail "unguarded.h local include was not detected"
grep -q "unguarded.h: guarded=no guard_style=none" "$OUT" || fail "unguarded.h unguarded status was not detected"

$PYTHON tools/leotuh_scan.py --stable-age 0 \
    --include-dir testdata/scan_include_path/include \
    testdata/scan_include_path/src/uses_shared.cpp > "$OUT" || exit 1

grep -q "local: SharedHeader.h" "$OUT" || fail "SharedHeader.h local include was not detected"
grep -q "SharedHeader.h: guarded=yes guard_style=ifndef_define" "$OUT" || fail "SharedHeader.h include-dir guard was not detected"

$PYTHON tools/leotuh_scan.py --stable-age 0 testdata/scan_risky_define/defines_this.cpp > "$OUT" || exit 1

grep -q "local_defines:" "$OUT" || fail "local_defines section was not printed"
grep -q "  this" "$OUT" || fail "this define was not detected"
grep -q "risky_local_defines:" "$OUT" || fail "risky_local_defines section was not printed"
grep -q "this:cpp_keyword_macro" "$OUT" || fail "this define was not classified as risky"

$PYTHON tools/leotuh_scan_tree.py --root testdata --stable-age 0 --include-dir testdata/scan_include_path/include > "$OUT" || exit 1

grep -q "sources_total:" "$OUT" || fail "tree scan did not print sources_total"
grep -q "local_headers_guarded:" "$OUT" || fail "tree scan did not print local_headers_guarded"
grep -q "risky_local_defines_total:" "$OUT" || fail "tree scan did not print risky_local_defines_total"

echo "PASS: LeoTUH scan smoke test"
