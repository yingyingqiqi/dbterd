import importlib.metadata
from typing import List

import click

from dbterd.adapters.worker import DbtWorker
from dbterd.cli import params
from dbterd.helpers import jsonify
from dbterd.helpers.log import logger

__version__ = importlib.metadata.version("dbterd")


# Programmatic invocation
class dbterdRunner:
    def __init__(self) -> None:
        pass

    def invoke(self, args: List[str]):
        try:
            dbt_ctx = dbterd.make_context(dbterd.name, args)
            return dbterd.invoke(dbt_ctx)
        except click.exceptions.Exit as e:
            # 0 exit code, expected for --version early exit
            if str(e) == "0":
                return [], True
            raise Exception(f"unhandled exit code {str(e)}")
        except (click.NoSuchOption, click.UsageError) as e:
            raise Exception(e.message)


# dbterd
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
    no_args_is_help=True,
    epilog="Specify one of these sub-commands and you can find more help from there.",
)
@click.version_option(__version__)
@click.pass_context
def dbterd(ctx, **kwargs):
    """Tools for producing diagram-as-code"""
    logger.info(f"Run with dbterd=={__version__}")


# dbterd debug
@dbterd.command(name="debug")
@click.pass_context
@params.common_params
def debug(ctx, **kwargs):
    """Inspect the hidden magics"""
    logger.info("**Arguments used**")
    logger.debug(jsonify.to_json(kwargs))
    logger.info("**Context used**")
    logger.debug(jsonify.to_json(ctx.obj))


# dbterd run
@dbterd.command(name="run")
@click.pass_context
@params.common_params
def run(ctx, **kwargs):
    """Run the convert"""
    DbtWorker(ctx).run(**kwargs)
