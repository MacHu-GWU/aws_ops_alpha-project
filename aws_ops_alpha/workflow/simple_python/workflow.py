# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``workflow.py`` module should have visualized logging.
"""

# standard library
import typing as T

# third party library (include vendor)
from ...vendor.emoji import Emoji
from ...vendor import semantic_branch as sem_branch

# modules from this project
from ...logger import logger
from ...runtime import runtime
from ...git import detect_semantic_branch

# modules from this submodule
from .constants import StepEnum, GitBranchNameEnum
from .rule import rule_set

# type hint
if T.TYPE_CHECKING:
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager


_semantic_branch_mapper = {
    GitBranchNameEnum.main: sem_branch.is_main_branch,
    GitBranchNameEnum.feature: sem_branch.is_feature_branch,
    GitBranchNameEnum.fix: sem_branch.is_fix_branch,
    GitBranchNameEnum.test: sem_branch.is_test_branch,
    GitBranchNameEnum.doc: sem_branch.is_doc_branch,
    GitBranchNameEnum.release: sem_branch.is_release_branch,
}


def _detect_semantic_branch(full_git_branch_name: str) -> str:
    return detect_semantic_branch(full_git_branch_name, _semantic_branch_mapper)


quiet = True if runtime.is_ci else False


def pip_install(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.pip_install(quiet=quiet, verbose=True)


def pip_install_dev(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.pip_install_dev(quiet=quiet, verbose=True)


def pip_install_test(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.pip_install_test(quiet=quiet, verbose=True)


def pip_install_doc(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.pip_install_doc(quiet=quiet, verbose=True)


def pip_install_automation(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.pip_install_automation(quiet=quiet, verbose=True)


def pip_install_all(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.pip_install_all(quiet=quiet, verbose=True)


def pip_install_all_in_ci(pyproject_ops: "pyops.PyProjectOps"):
    # if path_venv_bin_pytest already exists, it means that the virtualenv
    # is restored from cache, there's no need to install dependencies again.
    if pyproject_ops.path_venv_bin_pytest.exists() is False:
        pyproject_ops.pip_install_all(quiet=quiet, verbose=True)
    else:
        logger.info("dependencies are already installed, do nothing")


def poetry_lock(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.poetry_lock(verbose=True)


def poetry_export(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.poetry_export(verbose=True)


@logger.emoji_block(
    msg="Run Unit Test",
    emoji=Emoji.test,
)
def run_unit_test(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    check: bool = True,
):
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.RUN_CODE_COVERAGE_TEST,
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return
    pyproject_ops.run_unit_test()


@logger.emoji_block(
    msg="Run Code Coverage Test",
    emoji=Emoji.test,
)
def run_cov_test(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    check: bool = True,
):
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.RUN_CODE_COVERAGE_TEST,
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return
    pyproject_ops.run_cov_test()


def view_cov(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.view_cov(verbose=True)


@logger.emoji_block(
    msg="Build Documentation Site Locally",
    emoji=Emoji.doc,
)
def build_doc(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    check: bool = True,
):
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_DOCUMENTATION_WEBSITE,
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    pyproject_ops.build_doc()


def view_doc(pyproject_ops: "pyops.PyProjectOps"):
    pyproject_ops.view_doc()


@logger.emoji_block(
    msg="Deploy Documentation Site To S3 as Versioned Doc",
    emoji=Emoji.doc,
)
def deploy_versioned_doc(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    bsm_devops: "BotoSesManager",
    bucket: str,
    check: bool = True,
):
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_DOCUMENTATION_WEBSITE,
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    with bsm_devops.awscli():
        pyproject_ops.deploy_versioned_doc(bucket=bucket)


@logger.emoji_block(
    msg="Deploy Documentation Site To S3 as Latest Doc",
    emoji=Emoji.doc,
)
def deploy_latest_doc(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    bsm_devops: "BotoSesManager",
    bucket: str,
    check: bool = True,
):
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_DOCUMENTATION_WEBSITE,
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    with bsm_devops.awscli():
        pyproject_ops.deploy_latest_doc(bucket=bucket)


def view_latest_doc(
    pyproject_ops: "pyops.PyProjectOps",
    bucket: str,
):
    pyproject_ops.view_latest_doc(bucket=bucket)
