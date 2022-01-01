# Slugify Files & Directories

**A python application to slugify files & directories.**

## General Info

This project slugifies files & directories using
[slugify](https://github.com/un33k/python-slugify) and optionally tries to
compress the path, for easy distribution and (heavily opinionated) beautiful
looking folders. It's not the prettiest application ever, but it works and is in
a single file, for easy throwing around.

## Example

```bash
$ tree
.
├── BAZ Ä Ö Ü.txt
└── FOO
    └── FOO BAR.txt

1 directory, 2 files

$ slug -rz .
info: move ./BAZ Ä Ö Ü.txt to baz-ae-oe-ue.txt
info: move ./FOO to foo
info: move foo/FOO BAR.txt to bar.txt

$ tree
.
├── baz-ae-oe-ue.txt
└── foo
    └── bar.txt

1 directory, 2 files
```

## Installation

Download [slug.py](https://github.com/libaurea/slug/blob/main/slug.py).
Optionally create an alias in bash:

```bash
alias slug="/path/to/slug.py"
```

Or powershell:

```powershell
New-Alias slug "C:\Path\To\slug.py"
```

## Usage

```plaintext
usage: slug [-h] [-r] [-f | -F] [-z | -Z] [-s | -x | -c] [-n] [-d] [-v] path [path ...]

Slugify file and directory names

positional arguments:
  path                  paths to files and directories

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive       recurse into directories
  -f, --files           rename files only
  -F, --dirs            rename directories only
  -z, --compress        try to deduplicate path name (race condition)
  -Z, --force-compress  try to deduplicate entire path name
  -s, --standard        enable standard filter (default)
  -x, --posix           enable posix filter
  -c, --strict          enable strict filter
  -n, --dry-run         perform a trial run with no changes made
  -d, --debug           show debug output
  -v, --version         show program's version number and exit

example: slug -rn "File with Spaces.txt" "DIRECTORY"
```
