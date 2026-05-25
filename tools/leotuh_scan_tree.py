#!/usr/bin/env python
#
# LeoTUH tree scan reporter.
#
# This tool scans a source tree and prints conservative aggregate facts.
# It does not compile, link, emit aggregation files, or modify sources.

import os
import sys
import time
from optparse import OptionParser

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOL_DIR not in sys.path:
    sys.path.insert(0, TOOL_DIR)

import leotuh_scan


SOURCE_SUFFIXES = (".c", ".cc", ".cpp", ".cxx", ".m", ".mm")

DEFAULT_PRUNE_DIRS = {
    ".git": 1,
    "vendor": 1,
    "build": 1,
    "build-work": 1,
    "build/leotuh": 1,
}


def is_source(path):
    lower = path.lower()
    for suffix in SOURCE_SUFFIXES:
        if lower.endswith(suffix):
            return 1
    return 0


def should_prune_dir(name, extra_prune):
    if name in DEFAULT_PRUNE_DIRS:
        return 1
    if name in extra_prune:
        return 1
    return 0


def normalize_scan_path(path):
    path = os.path.normpath(path).replace(os.sep, "/")
    while path.startswith("./"):
        path = path[2:]
    if path == ".":
        return ""
    return path


def make_relative_path(path, root):
    path_abs = os.path.abspath(path)
    root_abs = os.path.abspath(root)

    if path_abs == root_abs:
        return ""

    prefix = root_abs + os.sep
    if path_abs.startswith(prefix):
        return path_abs[len(prefix):]

    return path


def prepare_exclude_paths(paths):
    result = []

    for path in paths:
        normalized = normalize_scan_path(path)
        if normalized:
            result.append(normalized)

    return result


def is_excluded_path(relative_path, exclude_paths):
    normalized = normalize_scan_path(relative_path)

    for exclude_path in exclude_paths:
        if normalized == exclude_path:
            return 1
        if normalized.startswith(exclude_path + "/"):
            return 1

    return 0


def collect_sources(root, extra_prune, exclude_paths):
    sources = []

    for dirpath, dirnames, filenames in os.walk(root):
        kept = []
        for dirname in dirnames:
            child_path = os.path.join(dirpath, dirname)
            child_rel = make_relative_path(child_path, root)

            if should_prune_dir(dirname, extra_prune):
                continue
            if is_excluded_path(child_rel, exclude_paths):
                continue

            kept.append(dirname)

        dirnames[:] = kept

        for filename in filenames:
            path = os.path.join(dirpath, filename)
            rel_path = make_relative_path(path, root)

            if is_excluded_path(rel_path, exclude_paths):
                continue

            if is_source(path):
                sources.append(os.path.normpath(path))

    sources.sort()
    return sources


def scan_one(path, include_dirs, stable_age):
    text = leotuh_scan.read_text(path)
    commentless = leotuh_scan.mask_comments_only(text)
    masked = leotuh_scan.mask_comments_and_strings(text)

    language = leotuh_scan.detect_language(path)
    approve, prohibit = leotuh_scan.find_markers(text)
    includes = leotuh_scan.find_direct_includes(commentless)
    defines = leotuh_scan.find_local_defines(commentless)
    risky_defines = leotuh_scan.find_risky_local_defines(defines)
    guards = leotuh_scan.find_local_header_guards(path, includes, include_dirs)
    has_entry_point = leotuh_scan.detect_entry_point(masked)

    mtime = os.path.getmtime(path)
    age = int(time.time() - mtime)
    recent = 1 if age < stable_age else 0

    return {
        "path": path,
        "language": language,
        "approve": approve,
        "prohibit": prohibit,
        "includes": includes,
        "defines": defines,
        "risky_defines": risky_defines,
        "guards": guards,
        "entry_point": has_entry_point,
        "recent": recent,
    }


def inc(stats, key, amount):
    stats[key] = stats.get(key, 0) + amount


def print_stat(stats, key):
    print("%s: %d" % (key, stats.get(key, 0)))


def read_scope_file(path):
    result = {
        "root": None,
        "include_dirs": [],
        "exclude_paths": [],
        "prune_dirs": [],
    }

    f = open(path, "r")
    try:
        text = f.read()
    finally:
        f.close()

    lineno = 0
    for raw_line in text.splitlines():
        lineno += 1
        line = raw_line.strip()

        if not line:
            continue
        if line.startswith("#"):
            continue

        if "=" not in line:
            raise ValueError("%s:%d: expected key=value" % (path, lineno))

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not value:
            raise ValueError("%s:%d: empty value for %s" % (path, lineno, key))

        if key == "root":
            result["root"] = value
        elif key == "include-dir":
            result["include_dirs"].append(value)
        elif key == "exclude-path":
            result["exclude_paths"].append(value)
        elif key == "prune":
            result["prune_dirs"].append(value)
        else:
            raise ValueError("%s:%d: unknown scope key: %s" % (path, lineno, key))

    return result


def main(argv):
    parser = OptionParser(
        usage="usage: %prog [options]",
        description="Scan a source tree and print aggregate LeoTUH facts."
    )
    parser.add_option(
        "--root",
        dest="root",
        default=".",
        help="source tree root"
    )
    parser.add_option(
        "--scope-file",
        dest="scope_file",
        default=None,
        help="read root, include-dir, exclude-path, and prune entries from a scope file"
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
    parser.add_option(
        "--prune",
        dest="prune_dirs",
        action="append",
        default=[],
        help="additional directory name to prune"
    )
    parser.add_option(
        "--exclude-path",
        dest="exclude_paths",
        action="append",
        default=[],
        help="root-relative path to exclude from scanning"
    )
    parser.add_option(
        "--list-risky",
        dest="list_risky",
        action="store_true",
        default=False,
        help="list files with risky local defines"
    )
    parser.add_option(
        "--list-missing",
        dest="list_missing",
        action="store_true",
        default=False,
        help="list missing local headers"
    )
    parser.add_option(
        "--list-unguarded",
        dest="list_unguarded",
        action="store_true",
        default=False,
        help="list unguarded local headers"
    )

    options, args = parser.parse_args(argv[1:])

    if args:
        parser.error("unexpected positional arguments")

    scope = {
        "root": None,
        "include_dirs": [],
        "exclude_paths": [],
        "prune_dirs": [],
    }

    if options.scope_file:
        if not os.path.isfile(options.scope_file):
            parser.error("scope file does not exist: %s" % options.scope_file)
        try:
            scope = read_scope_file(options.scope_file)
        except ValueError:
            error = sys.exc_info()[1]
            parser.error(str(error))

    root_value = options.root
    if options.root == "." and scope["root"]:
        root_value = scope["root"]

    root = os.path.normpath(root_value)
    if not os.path.isdir(root):
        parser.error("root directory does not exist: %s" % root)

    include_dirs = []
    include_dirs.extend(scope["include_dirs"])
    include_dirs.extend(options.include_dirs)

    extra_prune = {}
    for name in scope["prune_dirs"]:
        extra_prune[name] = 1
    for name in options.prune_dirs:
        extra_prune[name] = 1

    raw_exclude_paths = []
    raw_exclude_paths.extend(scope["exclude_paths"])
    raw_exclude_paths.extend(options.exclude_paths)
    exclude_paths = prepare_exclude_paths(raw_exclude_paths)

    sources = collect_sources(root, extra_prune, exclude_paths)

    stats = {}
    risky_lines = []
    missing_lines = []
    unguarded_lines = []

    inc(stats, "sources_total", len(sources))

    for source in sources:
        result = scan_one(source, include_dirs, options.stable_age)

        inc(stats, "sources_scanned", 1)

        if result["recent"]:
            inc(stats, "sources_recent", 1)
        else:
            inc(stats, "sources_stable", 1)

        if result["approve"]:
            inc(stats, "manual_approve", 1)
        if result["prohibit"]:
            inc(stats, "manual_prohibit", 1)
        if result["entry_point"]:
            inc(stats, "entry_points_detected", 1)
        if result["language"] == "unknown":
            inc(stats, "unknown_language", 1)

        inc(stats, "direct_includes_total", len(result["includes"]))
        inc(stats, "local_defines_total", len(result["defines"]))
        inc(stats, "risky_local_defines_total", len(result["risky_defines"]))

        if result["risky_defines"]:
            risky_lines.append("%s: %s" % (source, ", ".join(result["risky_defines"])))

        for name, header_path, guarded, style in result["guards"]:
            inc(stats, "local_headers_total", 1)

            if guarded == "yes":
                inc(stats, "local_headers_guarded", 1)
                if style == "pragma_once":
                    inc(stats, "local_headers_guarded_pragma_once", 1)
                elif style == "ifndef_define":
                    inc(stats, "local_headers_guarded_ifndef_define", 1)
            elif guarded == "missing":
                inc(stats, "local_headers_missing", 1)
                missing_lines.append("%s: %s -> %s" % (source, name, header_path))
            else:
                inc(stats, "local_headers_unguarded", 1)
                unguarded_lines.append("%s: %s -> %s" % (source, name, header_path))

    print("root: %s" % root)
    print("scope_file: %s" % (options.scope_file if options.scope_file else "none"))
    print("stable_age_seconds: %d" % options.stable_age)
    print("include_dirs:")
    if include_dirs:
        for include_dir in include_dirs:
            print("  %s" % include_dir)
    else:
        print("  none")

    print("exclude_paths:")
    if exclude_paths:
        for exclude_path in exclude_paths:
            print("  %s" % exclude_path)
    else:
        print("  none")

    print("")
    print("summary:")
    for key in [
        "sources_total",
        "sources_scanned",
        "sources_stable",
        "sources_recent",
        "manual_approve",
        "manual_prohibit",
        "entry_points_detected",
        "unknown_language",
        "direct_includes_total",
        "local_headers_total",
        "local_headers_guarded",
        "local_headers_guarded_ifndef_define",
        "local_headers_guarded_pragma_once",
        "local_headers_unguarded",
        "local_headers_missing",
        "local_defines_total",
        "risky_local_defines_total",
    ]:
        print_stat(stats, key)

    if options.list_risky:
        print("")
        print("risky_local_defines:")
        if risky_lines:
            for line in risky_lines:
                print("  %s" % line)
        else:
            print("  none")

    if options.list_missing:
        print("")
        print("missing_local_headers:")
        if missing_lines:
            for line in missing_lines:
                print("  %s" % line)
        else:
            print("  none")

    if options.list_unguarded:
        print("")
        print("unguarded_local_headers:")
        if unguarded_lines:
            for line in unguarded_lines:
                print("  %s" % line)
        else:
            print("  none")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
