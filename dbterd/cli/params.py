import functools

import click

from dbterd import default


def common_params(func):
    @click.option(
        "--artifacts-dir",
        "-ad",
        help="Specified the full path to dbt artifacts path which known as /target directory",
        default=default.default_artifact_path(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--manifest-path",
        "-mp",
        help="__DEPRECATED_WARNING__: Specified the full directory path to dbt manifest.json file. Use --artifacts-dir instead.",
        default=None,
        type=click.STRING,
    )
    @click.option(
        "--output",
        "-o",
        help="Output the result file. Default to the same target dir",
        default=default.default_output_path(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--select",
        "-s",
        help="Selecttion criteria. Support 'starts with' a string",
        default=None,
        type=click.STRING,
    )
    @click.option(
        "--exclude",
        "-ns",
        help="Exclusion criteria. Support 'not starts with' a string",
        default=None,
        type=click.STRING,
    )
    @click.option(
        "--target",
        "-t",
        help="Target to the diagram-as-code platform",
        default=default.default_target(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--algo",
        "-a",
        help="Specified algorithm in the way to detect diagram connectors",
        default=default.deafult_algo(),
        show_default=True,
        type=click.STRING,
    )
    @click.option(
        "--manifest-version",
        "-mv",
        help="Specified dbt manifest.json version",
        default=None,
        type=click.STRING,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # pragma: no cover

    return wrapper
