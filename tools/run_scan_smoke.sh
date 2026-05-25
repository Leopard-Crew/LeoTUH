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
grep -q "LOCAL_FLAG" "$OUT" || fail "LOCAL_FLAG define was not detected"

$PYTHON tools/leotuh_scan.py --stable-age 0 testdata/scan_noise/noise.cpp > "$OUT" || exit 1

grep -q "local: real.h" "$OUT" || fail "real.h local include was not detected"
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

echo "PASS: LeoTUH scan smoke test"
