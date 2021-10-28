from argparse import ArgumentParser
from pathlib import Path
import sys

from api_watchdog.collect import collect_results
from api_watchdog.core import WatchdogTest
from api_watchdog.runner import WatchdogRunner
from api_watchdog.hooks.result_group.mailgun import ResultGroupHookMailgun


def topological_print(result_group, file=None):
    file = file or sys.stdout
    for result in sorted(result_group.results, key=lambda g: g.test_name):
        print(
            f"{result.test_name:<20} {'Pass' if result.success else 'Fail'} {result.latency:<12.3f}",
            file=file,
        )
    for group in sorted(result_group.groups, key=lambda g: g.name):
        topological_print(group, file=file)

def discover(args):
    runner = WatchdogRunner()
    tests = [
        WatchdogTest.parse_file(p)
        for p in vars(args)['search-directory'].rglob(args.pattern)
    ]
    results = runner.run_tests(tests)
    grouped_results = collect_results(results)
    if args.email:
        email_hook = ResultGroupHookMailgun()
        email_hook(grouped_results)
    if args.output_path:
        with open(args.output_path, "w") as fp:
            fp.write(grouped_results.json())
    else:
        topological_print(grouped_results)

def cli():
    parser = ArgumentParser(description="API Watchdog CLI")
    subparsers = parser.add_subparsers()

    parser_discover = subparsers.add_parser(
        "discover", help="Discover and run tests in a directory"
    )
    parser_discover.add_argument(
        "search-directory",
        type=Path,
        help="Directory to recursively search for tests",
    )
    parser_discover.add_argument(
        "--pattern",
        "-p",
        type=str,
        default="*.watchdog.json",
        help="glob style pattern to match against for tests",
    )
    parser_discover.add_argument(
        "--output_path",
        "-o",
        type=Path,
        default=None,
        help="Path to output test results file. When not provided, results are"
        " sent to stdout",
    )
    parser_discover.add_argument(
        "--email",
        action="store_true"
    )
    parser_discover.set_defaults(func=discover)

    args = parser.parse_args()
    args.func(args)
