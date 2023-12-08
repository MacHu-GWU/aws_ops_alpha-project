# -*- coding: utf-8 -*-

"""
如何区分
"""

import typing as T
import os
import subprocess
from pathlib import Path

import pyproject_ops.api as pyops
import aws_console_url.api as aws_console_url
import aws_lambda_layer.api as aws_lambda_layer

from .vendor.emoji import Emoji
from .vendor.better_pathlib import temp_cwd
from .logger import logger

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path


def build_lambda_source(
    pyproject_ops: pyops.PyProjectOps,
    verbose: bool = True,
) -> T.Tuple[str, Path]:
    """
    Wrapper of ``aws_lambda_layer.api.build_source_artifacts``.

    Build lambda source artifacts locally and return source code sha256 and zip file path.
    It will NOT upload the artifacts to S3.

    :return: tuple of two items: (source code sha256, zip file path)
    """
    path_lambda_function = pyproject_ops.dir_lambda_app.joinpath("lambda_function.py")
    source_sha256, path_source_zip = aws_lambda_layer.build_source_artifacts(
        path_setup_py_or_pyproject_toml=pyproject_ops.path_pyproject_toml,
        package_name=pyproject_ops.package_name,
        path_lambda_function=path_lambda_function,
        dir_build=pyproject_ops.dir_build_lambda,
        use_pathlib=True,
        verbose=verbose,
    )
    return source_sha256, path_source_zip


def deploy_layer(
    bsm_devops: "BotoSesManager",
    pyproject_ops: pyops.PyProjectOps,
    layer_name: str,
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
) -> T.Optional[aws_lambda_layer.LayerDeployment]:
    """
    Publish lambda layer.

    This function doesn't have any logging, it can make the final function shorter.
    """
    return aws_lambda_layer.deploy_layer(
        bsm=bsm_devops,
        layer_name=layer_name,
        python_versions=[
            f"python{pyproject_ops.python_version}",
        ],
        path_requirements=pyproject_ops.path_requirements,
        dir_build=pyproject_ops.dir_build_lambda,
        s3dir_lambda=s3dir_lambda,
        bin_pip=pyproject_ops.path_venv_bin_pip,
        quiet=True,
        tags=tags,
    )



def grant_layer_permission(
    bsm_devops: "BotoSesManager",
    workload_bsm_list: T.List["BotoSesManager"],
    layer_deployment: aws_lambda_layer.LayerDeployment,
):
    layer_name = layer_deployment.layer_version_arn.split(":")[6]
    for bsm_workload in workload_bsm_list:
        aws_lambda_layer.grant_layer_permission(
            bsm=bsm_devops,
            layer_name=layer_name,
            version_number=layer_deployment.layer_version,
            principal=bsm_workload.aws_account_id,
        )


@logger.start_and_end(
    msg="Build Lambda Layer Artifacts",
    start_emoji=f"{Emoji.build} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def build_lambda_layer(
    check=True,
):
    if check:
        if (
            aws_ops_alpha.simple_lambda.do_we_deploy_lambda_layer(
                is_ci_runtime=runtime.is_ci,
                branch_name=git_repo.git_branch_name,
                is_layer_branch=git_repo.is_layer_branch,
            )
            is False
        ):
            return

    bsm_devops = boto_ses_factory.bsm_devops
    layer_name = config.env.lambda_layer_name
    layer_deployment = _build_lambda_layer(
        bsm=bsm_devops,
        layer_name=layer_name,
        s3dir_lambda=config.env.s3dir_lambda,
        tags=config.env.devops_aws_tags,
    )
    if layer_deployment is None:
        logger.info(
            f"{Emoji.red_circle} don't publish layer, "
            f"the current requirements.txt is the same as the one "
            f"of the latest lambda layer."
        )
    else:
        logger.info(f"published a new layer version: {layer_deployment.layer_version}")
        logger.info(f"published layer arn: {layer_deployment.layer_version_arn}")
        layer_console_url = (
            f"https://{bsm_devops.aws_region}.console.aws.amazon.com/lambda"
            f"/home?region={bsm_devops.aws_region}#"
            f"/layers?fo=and&o0=%3A&v0={layer_name}"
        )
        logger.info(f"preview deployed layer at {layer_console_url}")
        console_url = layer_deployment.s3path_layer_zip.console_url
        logger.info(f"preview layer.zip at {console_url}")
        console_url = layer_deployment.s3path_layer_requirements_txt.console_url
        logger.info(f"preview requirements.txt at {console_url}")

        for bsm_workload in boto_ses_factory.workload_bsm_list:
            aws_lambda_layer.grant_layer_permission(
                bsm=bsm_devops,
                layer_name=layer_name,
                version_number=layer_deployment.layer_version,
                principal=bsm_workload.aws_account_id,
            )
