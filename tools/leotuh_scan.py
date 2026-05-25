#!/usr/bin/env python
#
# LeoTUH scan-only helper.
#
# This tool performs a conservative first-pass source scan.
# It does not compile, link, emit aggregation files, or modify sources.

import os
import re
import sys
import time
from optparse import OptionParser


SOURCE_EXTENSIONS = {
    ".c": "c",
    ".cc": "c++",
    ".cpp": "c++",
    ".cxx": "c++",
    ".m": "objective-c",
    ".mm": "objective-c++",
}


RISKY_LOCAL_DEFINE_NAMES = {
    "this": "cpp_keyword_macro"
}


def read_text(path):
    f = open(path, "rb")
    try:
        data = f.read()
    finally:
        f.close()

    # Keep this simple and Leopard-safe.
    # Python 2 returns str here. Python 3 returns bytes and needs decoding.
    if not isinstance(data, str):
        data = data.decode("utf-8", "replace")

    return data


def detect_language(path):
    ext = os.path.splitext(path)[1].lower()
    return SOURCE_EXTENSIONS.get(ext, "unknown")


def find_markers(text):
    approve = 0
    prohibit = 0

    for line in text.splitlines():
        if "LEO_TUH_APPROVE" in line:
            approve = 1
        if "LEO_TUH_PROHIBIT" in line:
            prohibit = 1

    return approve, prohibit


def mask_comments_and_strings(text):
    # Replace comments and string/char literals with whitespace while preserving line breaks.
    out = []
    i = 0
    n = len(text)
    state = "normal"

    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if state == "normal":
            if c == "/" and nxt == "/":
                out.append(" ")
                out.append(" ")
                i += 2
                state = "line_comment"
                continue
            if c == "/" and nxt == "*":
                out.append(" ")
                out.append(" ")
                i += 2
                state = "block_comment"
                continue
            if c == '"':
                out.append(" ")
                i += 1
                state = "string"
                continue
            if c == "'":
                out.append(" ")
                i += 1
                state = "char"
                continue
            out.append(c)
            i += 1
            continue

        if state == "line_comment":
            if c == "\n":
                out.append("\n")
                state = "normal"
            else:
                out.append(" ")
            i += 1
            continue

        if state == "block_comment":
            if c == "*" and nxt == "/":
                out.append(" ")
                out.append(" ")
                i += 2
                state = "normal"
                continue
            if c == "\n":
                out.append("\n")
            else:
                out.append(" ")
            i += 1
            continue

        if state == "string":
            if c == "\\":
                out.append(" ")
                if i + 1 < n:
                    out.append(" ")
                    i += 2
                else:
                    i += 1
                continue
            if c == '"':
                out.append(" ")
                state = "normal"
            elif c == "\n":
                out.append("\n")
                state = "normal"
            else:
                out.append(" ")
            i += 1
            continue

        if state == "char":
            if c == "\\":
                out.append(" ")
                if i + 1 < n:
                    out.append(" ")
                    i += 2
                else:
                    i += 1
                continue
            if c == "'":
                out.append(" ")
                state = "normal"
            elif c == "\n":
                out.append("\n")
                state = "normal"
            else:
                out.append(" ")
            i += 1
            continue

    return "".join(out)


def mask_comments_only(text):
    # Replace comments with whitespace while preserving strings and char literals.
    # This is needed for #include "local.h", where the quoted header name is syntax.
    out = []
    i = 0
    n = len(text)
    state = "normal"

    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if state == "normal":
            if c == "/" and nxt == "/":
                out.append(" ")
                out.append(" ")
                i += 2
                state = "line_comment"
                continue
            if c == "/" and nxt == "*":
                out.append(" ")
                out.append(" ")
                i += 2
                state = "block_comment"
                continue
            if c == '"':
                out.append(c)
                i += 1
                state = "string"
                continue
            if c == "'":
                out.append(c)
                i += 1
                state = "char"
                continue

            out.append(c)
            i += 1
            continue

        if state == "line_comment":
            if c == "\n":
                out.append("\n")
                state = "normal"
            else:
                out.append(" ")
            i += 1
            continue

        if state == "block_comment":
            if c == "*" and nxt == "/":
                out.append(" ")
                out.append(" ")
                i += 2
                state = "normal"
                continue
            if c == "\n":
                out.append("\n")
            else:
                out.append(" ")
            i += 1
            continue

        if state == "string":
            out.append(c)
            if c == "\\":
                if i + 1 < n:
                    out.append(text[i + 1])
                    i += 2
                else:
                    i += 1
                continue
            if c == '"':
                state = "normal"
            elif c == "\n":
                state = "normal"
            i += 1
            continue

        if state == "char":
            out.append(c)
            if c == "\\":
                if i + 1 < n:
                    out.append(text[i + 1])
                    i += 2
                else:
                    i += 1
                continue
            if c == "'":
                state = "normal"
            elif c == "\n":
                state = "normal"
            i += 1
            continue

    return "".join(out)


def find_direct_includes(commentless_text):
    includes = []

    include_re = re.compile(r'^\s*#\s*include\s*"([^"]+)"')
    system_re = re.compile(r'^\s*#\s*include\s*<([^>]+)>')

    for line in commentless_text.splitlines():
        m = include_re.search(line)
        if m:
            includes.append(("local", m.group(1)))
            continue

        m = system_re.search(line)
        if m:
            includes.append(("system", m.group(1)))
            continue

    return includes


def find_local_defines(commentless_text):
    defines = []
    define_re = re.compile(r'^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)')

    for line in commentless_text.splitlines():
        m = define_re.search(line)
        if m:
            name = m.group(1)
            if name not in defines:
                defines.append(name)

    return defines


def find_risky_local_defines(defines):
    risky = []

    for name in defines:
        if name in RISKY_LOCAL_DEFINE_NAMES:
            risky.append("%s:%s" % (name, RISKY_LOCAL_DEFINE_NAMES[name]))

    return risky


def classify_candidate(recent, approve, prohibit, has_entry_point, local_header_guards, risky_defines):
    blockers = []

    if recent:
        blockers.append("recent_file")

    if prohibit:
        blockers.append("manual_prohibit")

    if has_entry_point:
        blockers.append("entry_point")

    for name, header_path, guarded, style in local_header_guards:
        if guarded == "missing":
            blockers.append("missing_local_header:%s" % name)
        elif guarded == "no":
            blockers.append("unguarded_local_header:%s" % name)

    for risky in risky_defines:
        blockers.append("risky_local_define:%s" % risky)

    if blockers:
        return ("no", blockers)

    return ("yes", blockers)


def detect_entry_point(masked_text):
    patterns = [
        r'\bmain\s*\(',
        r'\bAPP_MAIN\s*\(',
        r'\bGUI_APP_MAIN\s*\(',
        r'\bCONSOLE_APP_MAIN\s*\(',
    ]

    for pattern in patterns:
        if re.search(pattern, masked_text):
            return 1

    return 0


def resolve_local_include(source_path, include_name, include_dirs):
    source_dir = os.path.dirname(source_path)

    candidates = [
        os.path.normpath(os.path.join(source_dir, include_name))
    ]

    for include_dir in include_dirs:
        candidates.append(os.path.normpath(os.path.join(include_dir, include_name)))

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    return candidates[0]


def detect_header_guard(header_path):
    if not os.path.isfile(header_path):
        return ("missing", "not_found")

    text = read_text(header_path)
    commentless = mask_comments_only(text)
    lines = commentless.splitlines()

    pragma_once_re = re.compile(r'^\s*#\s*pragma\s+once\b')
    ifndef_re = re.compile(r'^\s*#\s*ifndef\s+([A-Za-z_][A-Za-z0-9_]*)\b')
    define_re = re.compile(r'^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\b')

    limit = min(len(lines), 80)

    for i in range(0, limit):
        if pragma_once_re.search(lines[i]):
            return ("yes", "pragma_once")

    for i in range(0, limit):
        m = ifndef_re.search(lines[i])
        if not m:
            continue

        guard_name = m.group(1)
        search_limit = min(len(lines), i + 10)

        for j in range(i + 1, search_limit):
            m2 = define_re.search(lines[j])
            if m2 and m2.group(1) == guard_name:
                return ("yes", "ifndef_define")

    return ("no", "none")


def find_local_header_guards(source_path, includes, include_dirs):
    guards = []

    for kind, name in includes:
        if kind != "local":
            continue

        header_path = resolve_local_include(source_path, name, include_dirs)
        guarded, style = detect_header_guard(header_path)
        guards.append((name, header_path, guarded, style))

    return guards


def print_list(title, values):
    print("%s:" % title)
    if not values:
        print("  none")
        return

    for value in values:
        if isinstance(value, tuple):
            print("  %s: %s" % (value[0], value[1]))
        else:
            print("  %s" % value)


def print_header_guards(values):
    print("local_header_guards:")
    if not values:
        print("  none")
        return

    for name, path, guarded, style in values:
        print("  %s: guarded=%s guard_style=%s path=%s" % (name, guarded, style, path))


def main(argv):
    parser = OptionParser(
        usage="usage: %prog [options] SOURCE",
        description="Scan one source file and print conservative LeoTUH facts."
    )
    parser.add_option(
        "--stable-age",
        dest="stable_age",
        type="int",
        default=3600,
        help="minimum age in seconds before a file is considered stable"
    )
    parser.add_option(
        "--include-dir",
        dest="include_dirs",
        action="append",
        default=[],
        help="additional include directory for resolving local headers"
    )

    options, args = parser.parse_args(argv[1:])

    if len(args) != 1:
        parser.error("exactly one source file is required")

    path = args[0]

    if not os.path.isfile(path):
        parser.error("source file does not exist: %s" % path)

    text = read_text(path)
    commentless = mask_comments_only(text)
    masked = mask_comments_and_strings(text)

    language = detect_language(path)
    approve, prohibit = find_markers(text)
    includes = find_direct_includes(commentless)
    defines = find_local_defines(commentless)
    risky_defines = find_risky_local_defines(defines)
    local_header_guards = find_local_header_guards(path, includes, options.include_dirs)
    has_entry_point = detect_entry_point(masked)

    mtime = os.path.getmtime(path)
    age = int(time.time() - mtime)
    recent = 1 if age < options.stable_age else 0

    decision = "report_only"
    reason = "candidate_classification_only"

    if prohibit:
        decision = "excluded"
        reason = "manual_prohibit"
    elif recent:
        decision = "excluded"
        reason = "too_recent"
    elif has_entry_point:
        decision = "excluded"
        reason = "entry_point_detected"
    elif language == "unknown":
        decision = "excluded"
        reason = "unknown_language"

    candidate, candidate_blockers = classify_candidate(
        recent,
        approve,
        prohibit,
        has_entry_point,
        local_header_guards,
        risky_defines
    )

    print("path: %s" % path)
    print("language: %s" % language)
    print("mtime: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)))
    print("age_seconds: %d" % age)
    print("stable_age_seconds: %d" % options.stable_age)
    print("recent: %s" % ("yes" if recent else "no"))
    print("marker_approve: %s" % ("yes" if approve else "no"))
    print("marker_prohibit: %s" % ("yes" if prohibit else "no"))
    print("entry_point_detected: %s" % ("yes" if has_entry_point else "no"))
    print_list("include_dirs", options.include_dirs)
    print_list("direct_includes", includes)
    print_header_guards(local_header_guards)
    print_list("local_defines", defines)
    print_list("risky_local_defines", risky_defines)
    print("candidate: %s" % candidate)
    print_list("candidate_blockers", candidate_blockers)
    print("decision: %s" % decision)
    print("reason: %s" % reason)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
