# -*- coding: utf-8 -*-

"""
This module implements the automation to deploy CloudFormation stack via CDK.
"""

import typing as T
import os
import subprocess
from pathlib import Path

import aws_console_url.api as aws_console_url

from .vendor.emoji import Emoji
from .vendor.better_pathlib import temp_cwd
from .logger import logger

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager


@logger.emoji_block(
    msg="Run 'cdk deploy'",
    emoji=Emoji.cloudformation,
)
def cdk_deploy(
    env_name: str,
    bsm: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
):
    """
    Run ``cdk deploy ...`` command.
    """
    logger.info(f"deploy cloudformation to {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")
    with bsm.awscli():
        os.environ["USER_ENV_NAME"] = env_name
        args = ["cdk", "deploy"]
        if skip_prompt is True:
            args.extend(["--require-approval", "never"])
        with temp_cwd(dir_cdk):
            subprocess.run(args, check=True)


@logger.emoji_block(
    msg="Run 'cdk destroy'",
    emoji=Emoji.cloudformation,
)
def cdk_destroy(
    env_name: str,
    bsm: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
):
    """
    Run ``cdk destroy ...`` command.
    """
    logger.info(f"delete cloudformation from {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")
    with bsm.awscli():
        os.environ["USER_ENV_NAME"] = env_name
        args = ["cdk", "destroy"]
        if skip_prompt is True:
            args.extend(["--force"])
        with temp_cwd(dir_cdk):
            subprocess.run(args, check=True)
