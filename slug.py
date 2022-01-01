import argparse
from os import system
from pathlib import Path
from typing import Iterable

from slugify import slugify


class Constant:
    DEBUG_SKIP = "skip %s/\033[1;33m%s\033[0m"
    INFO_DRY_RUN = "dry run"
    INFO_RENAME = "move %s/\033[1;35m%s\033[0m to \033[1;32m%s\033[0m"

    LOGGER_DEBUG = "\033[1;33mdebug:\033[0m %s"
    LOGGER_INFO = "\033[1;32minfo:\033[0m %s"
    LOGGER_WARN = "\033[1;31mwarn:\033[0m %s"

    REGEX_POSIX = r"[^a-zA-Z0-9_.-]+"
    REGEX_STANDARD = r"[^a-z0-9.-]+"
    REGEX_STRICT = None

    REPLACEMENTS = [
        ["Ü", "ue"],
        ["ü", "ue"],
        ["Ä", "ae"],
        ["ä", "ae"],
        ["Ö", "oe"],
        ["ö", "oe"],
        ["\'", ""]
    ]

    SEPARATOR = "-"

    VERSION = "slug 1.0"

    WARN_CONFLICT = "conflict %s/\033[1;35m%s\033[0m to \033[1;31m%s\033[0m"
    WARN_UNKNOWN_TYPE = "unknown or broken type %s/\033[1;31m%s\033[0m"


class Logger:
    @staticmethod
    def debug(message: str) -> None:
        print(Constant.LOGGER_DEBUG % message)

    @staticmethod
    def info(message: str) -> None:
        print(Constant.LOGGER_INFO % message)

    @staticmethod
    def warn(message: str) -> None:
        print(Constant.LOGGER_WARN % message)


class Parser:
    ARGUMENTS = argparse.ArgumentParser(
        prog="slug",
        description="Slugify file and directory names",
        epilog="example: slug -rn \"File with Spaces.txt\" \"DIRECTORY\"",
        allow_abbrev=False)
    ARGUMENTS.add_argument("-r", "--recursive",
                           action="store_true",
                           help="recurse into directories",
                           default=False)
    IGNORES = ARGUMENTS.add_mutually_exclusive_group()
    IGNORES.add_argument("-f", "--files",
                         action="store_true",
                         help="rename files only",
                         default=False)
    IGNORES.add_argument("-F", "--dirs",
                         action="store_true",
                         help="rename directories only",
                         default=False)
    COMPRESS = ARGUMENTS.add_mutually_exclusive_group()
    COMPRESS.add_argument("-z", "--compress",
                          action="store_true",
                          help="try to deduplicate path name (race condition)",
                          default=False)
    COMPRESS.add_argument("-Z", "--force-compress",
                          action="store_true",
                          help="try to deduplicate entire path name",
                          default=False)
    FILTERS = ARGUMENTS.add_mutually_exclusive_group()
    FILTERS.add_argument("-s", "--standard",
                         action="store_true",
                         help="enable standard filter (default)",
                         default=False)
    FILTERS.add_argument("-x", "--posix",
                         action="store_true",
                         help="enable posix filter",
                         default=False)
    FILTERS.add_argument("-c", "--strict",
                         action="store_true",
                         help="enable strict filter",
                         default=False)
    ARGUMENTS.add_argument("-n", "--dry-run",
                           action="store_true",
                           help="perform a trial run with no changes made",
                           default=False)
    ARGUMENTS.add_argument("-d", "--debug",
                           action="store_true",
                           help="show debug output",
                           default=False)
    ARGUMENTS.add_argument("-v", "--version",
                           action="version",
                           version=Constant.VERSION)
    ARGUMENTS.add_argument("path",
                           metavar="path",
                           type=str,
                           nargs="+",
                           help="paths to files and directories")

    argument = None
    recursive = None
    files = None
    dirs = None
    standard_compress = None
    force_compress = None
    filter = None
    dry_run = None
    debug = None
    path = None

    def __init__(self, argument: argparse.Namespace) -> None:
        if argument.debug:
            Logger.debug(argument)

        self.argument = argument
        self.recursive = argument.recursive
        self.files = argument.files
        self.dirs = argument.dirs
        self.standard_compress = argument.compress
        self.force_compress = argument.force_compress
        self.dry_run = argument.dry_run
        self.debug = argument.debug
        self.path = argument.path

        if argument.strict:
            self.filter = Constant.REGEX_STRICT
        elif argument.posix:
            self.filter = Constant.REGEX_POSIX
        else:
            self.filter = Constant.REGEX_STANDARD

    def lowercase(self) -> bool:
        return not self.argument.posix

    def file(self) -> bool:
        return not self.dirs

    def directory(self) -> bool:
        return not self.files


class Transformer:
    @staticmethod
    def stopwords(path: Path) -> Iterable[str]:
        if parser.force_compress:
            return Transformer.slug(path.parent.as_posix()).split(Constant.SEPARATOR)
        elif parser.standard_compress:
            return Transformer.slug(path.parent.name).split(Constant.SEPARATOR)
        else:
            return ()

    @staticmethod
    def slug(text: str, stopwords: Iterable[str] = ()) -> str:
        result = slugify(text=text,
                         entities=True,
                         decimal=True,
                         hexadecimal=True,
                         max_length=0,
                         word_boundary=False,
                         separator=Constant.SEPARATOR,
                         save_order=False,
                         stopwords=stopwords,
                         regex_pattern=parser.filter,
                         lowercase=parser.lowercase(),
                         replacements=Constant.REPLACEMENTS)
        return result

    @staticmethod
    def rename(source: Path, destination: Path) -> Path:
        if source.as_posix() != destination.as_posix():
            # Allow simple case change, but not windows conflicts
            if destination.exists() and source.as_posix().lower() != destination.as_posix().lower():
                Logger.warn(Constant.WARN_CONFLICT %
                            (source.parent.as_posix(), source.name, destination.name))
            else:
                Logger.info(Constant.INFO_RENAME %
                            (source.parent.as_posix(), source.name, destination.name))
                if not parser.dry_run:
                    return source.rename(destination)
        elif parser.debug:
            Logger.debug(Constant.DEBUG_SKIP %
                         (source.parent.as_posix(), source.name))
        return source

    @staticmethod
    def rename_file(file: Path) -> Path:
        if parser.file():
            result = Path(file.parent,
                          Transformer.slug(file.stem, Transformer.stopwords(file)) + file.suffix.lower())
            return Transformer.rename(file, result)
        else:
            return file

    @staticmethod
    def rename_dir(directory: Path) -> Path:
        if parser.directory():
            result = Path(directory.parent,
                          Transformer.slug(directory.name, Transformer.stopwords(directory)))
            return Transformer.rename(directory, result)
        else:
            return directory

    @staticmethod
    def traverse(path: Path) -> None:
        for p in path.iterdir():
            if p.is_file():
                Transformer.rename_file(p)
            elif p.is_dir():
                directory = Transformer.rename_dir(p)
                if parser.recursive:
                    Transformer.traverse(directory)
            else:
                Logger.warn(Constant.WARN_UNKNOWN_TYPE %
                            (p.parent.as_posix(), p.name))


def main() -> None:
    system("color")
    global parser
    parser = Parser(Parser.ARGUMENTS.parse_args())

    if parser.dry_run:
        Logger.info(Constant.INFO_DRY_RUN)

    for path in parser.path:
        Transformer.traverse(Path(path))


main()
