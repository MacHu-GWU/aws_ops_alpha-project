# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``workflow.py`` module should have visualized logging.
"""

# standard library
import typing as T
import time
from pathlib import Path

# third party library (include vendor)
import aws_console_url.api as aws_console_url
from ...vendor.emoji import Emoji
from ...vendor.aws_lambda_version_and_alias import publish_version
from ...vendor import semantic_branch as sem_branch

# modules from this project
from ...logger import logger
from ...git import detect_semantic_branch
from ...aws_helpers import aws_cdk_helpers, aws_lambda_helpers
from ...runtime import RunTimeEnum
from ...environment import EnvEnum

# modules from this submodule
from .constants import StepEnum, GitBranchNameEnum
from .rule import rule_set

# type hint
if T.TYPE_CHECKING:
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path


def is_layer_branch(name: str) -> bool:
    return sem_branch.is_certain_semantic_branch(name, ["layer"])


def is_app_branch(name: str) -> bool:
    # todo, branch name could be app-123
    return sem_branch.is_certain_semantic_branch(name, ["app"])


_semantic_branch_mapper = {
    GitBranchNameEnum.main: sem_branch.is_main_branch,
    GitBranchNameEnum.feature: sem_branch.is_feature_branch,
    GitBranchNameEnum.fix: sem_branch.is_fix_branch,
    GitBranchNameEnum.doc: sem_branch.is_doc_branch,
    GitBranchNameEnum.layer: is_layer_branch,
    GitBranchNameEnum.app: is_app_branch,
    GitBranchNameEnum.release: sem_branch.is_release_branch,
    GitBranchNameEnum.cleanup: sem_branch.is_cleanup_branch,
}


def _detect_semantic_branch(full_git_branch_name: str) -> str:
    return detect_semantic_branch(full_git_branch_name, _semantic_branch_mapper)


@logger.start_and_end(
    msg="Build Lambda Source Artifacts",
    start_emoji=f"{Emoji.build} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def build_lambda_source(
    pyproject_ops: "pyops.PyProjectOps",
    verbose: bool = False,
):
    source_sha256, path_source_zip = aws_lambda_helpers.build_lambda_source(
        pyproject_ops=pyproject_ops,
        verbose=verbose,
    )
    logger.info(f"review source artifacts at local: {path_source_zip}")
    logger.info(f"review source artifacts sha256: {source_sha256}")


@logger.start_and_end(
    msg="Build Lambda Layer Artifacts",
    start_emoji=f"{Emoji.build} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def publish_lambda_layer(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    bsm_devops: "BotoSesManager",
    workload_bsm_list: T.List["BotoSesManager"],
    pyproject_ops: "pyops.PyProjectOps",
    layer_name: str,
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
    check=True,
):
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_LAMBDA_LAYER,
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    layer_deployment = aws_lambda_helpers.deploy_layer(
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        layer_name=layer_name,
        s3dir_lambda=s3dir_lambda,
        tags=tags,
    )

    aws_lambda_helpers.explain_layer_deployment(
        bsm_devops=bsm_devops,
        layer_deployment=layer_deployment,
    )

    if layer_deployment is not None:
        aws_lambda_helpers.grant_layer_permission(
            bsm_devops=bsm_devops,
            workload_bsm_list=workload_bsm_list,
            layer_deployment=layer_deployment,
        )

    return layer_deployment


@logger.emoji_block(
    msg="Publish new Lambda version",
    emoji=Emoji.awslambda,
)
def publish_lambda_version(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    bsm_workload: "BotoSesManager",
    lbd_func_name_list: T.List[str],
    check=True,
):
    """
    Publish a new lambda version from latest.
    """
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_NEW_LAMBDA_VERSION,
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    for lbd_func_name in lbd_func_name_list:
        url = aws_console.awslambda.get_function(lbd_func_name)
        logger.info(f"preview lambda function {lbd_func_name!r}: {url}", 1)
        publish_version(lbd_client=bsm_workload.lambda_client, func_name=lbd_func_name)


@logger.start_and_end(
    msg="Deploy App",
    start_emoji=f"{Emoji.deploy}",
    error_emoji=f"{Emoji.failed} {Emoji.deploy}",
    end_emoji=f"{Emoji.succeeded} {Emoji.deploy}",
    pipe=Emoji.deploy,
)
def deploy_app(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    bsm_workload: "BotoSesManager",
    lbd_func_name_list: T.List[str],
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
):
    logger.info(f"deploy app to {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")

    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.DEPLOY_LAMBDA_APP_VIA_CDK,
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    with logger.nested():
        build_lambda_source()
        aws_cdk_helpers.cdk_deploy(
            bsm_workload=bsm_workload,
            dir_cdk=dir_cdk,
            env_name=env_name,
            skip_prompt=skip_prompt,
        )
        publish_lambda_version(
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
            bsm_workload=bsm_workload,
            lbd_func_name_list=lbd_func_name_list,
        )


@logger.start_and_end(
    msg="Delete App",
    start_emoji=f"{Emoji.delete}",
    error_emoji=f"{Emoji.failed} {Emoji.delete}",
    end_emoji=f"{Emoji.succeeded} {Emoji.delete}",
    pipe=Emoji.delete,
)
def delete_app(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
):
    logger.info(f"delete app from {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")

    if check:
        _mapper = {
            EnvEnum.devops.value: StepEnum.DELETE_LAMBDA_APP_IN_SBX.value,
            EnvEnum.sbx.value: StepEnum.DELETE_LAMBDA_APP_IN_SBX.value,
            EnvEnum.tst.value: StepEnum.DELETE_LAMBDA_APP_IN_TST.value,
            EnvEnum.stg.value: StepEnum.DELETE_LAMBDA_APP_IN_STG.value,
            EnvEnum.prd.value: StepEnum.DELETE_LAMBDA_APP_IN_PRD.value,
        }

        flag = rule_set.should_we_do_it(
            step=_mapper[env_name],
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    with logger.nested():
        aws_cdk_helpers.cdk_destroy(
            bsm_workload=bsm_workload,
            dir_cdk=dir_cdk,
            env_name=env_name,
            skip_prompt=skip_prompt,
        )


@logger.emoji_block(
    msg="Run Integration Test",
    emoji=Emoji.test,
)
def run_int_test(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    wait: bool = False,
    check: bool = True,
):
    logger.info(f"Run integration test in {env_name!r} env...")
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.RUN_INTEGRATION_TEST,
            git_branch_name=_detect_semantic_branch(git_branch_name),
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    # you may want to wait a few seconds for the CDK deployment taking effect
    # you should do this in CI environment if you run integration test
    # right after ``cdk deploy``
    if wait:
        time.sleep(5)
    pyproject_ops.run_int_test()


# from ..rule1 import (
#     only_execute_on_certain_branch,
#     only_execute_on_certain_runtime,
#     only_execute_on_certain_env,
#     log_why_not_run_integration_test_in_prod,
#     confirm_to_proceed_in_prod,
#     only_execute_on_certain_runtime_branch_env,
#     log_why_not_create_git_tag_in_non_prod,
#     log_why_not_create_git_tag_in_local,
# )
# from ..runtime import RunTimeEnum
#
# from . import simple_python
#
#
# class StepEnum(str, enum.Enum):
#     """
#     Explains:
#
#     1. Create Python virtual environment.
#     2. Install all Python dependencies, reuse cache if possible.
#     3. Run code coverage test.
#     4. Publish documentation website from the latest code if needed.
#     5. Publish Lambda layer version for Python dependencies if needed.
#     6. If developer are on an isolated sandbox branch, then deploy Lambda app to it.
#     7. If developer are on an isolated sandbox branch, then run integration test on it.
#     8. Deploy Lambda app to sandbox.
#     9. Run integration test in sandbox.
#
#     If you are not doing a release, this is the end of the pipeline.
#
#     Below are additional steps for release:
#
#     10. Deploy Lambda app to test environment.
#     11. Run integration test in test environment.
#     12. Deploy Lambda app to prod.
#     13. Run integration test in prod, if needed.
#     14. Create an immutable config snapshot, so we can roll back anytime.
#     15. Create a git tag, so we can roll back anytime.
#
#     This is the end of the pipeline for release.
#
#     If you no longer need this project, you may want to clean up all the deployment.
#
#     16. Delete Lambda app from isolated sandbox branch after your PR is merged.
#     17. Delete Lambda app from sandbox.
#     18. Delete Lambda app from test environment.
#     19. Delete Lambda app from prod.
#     """
#
#     # fmt: off
#     s01_create_virtualenv = "01 - 🐍 Create Virtualenv"
#     s02_install_dependencies = "02 - 💾 Install Dependencies"
#     s03_run_code_coverage_test = "03 - 🧪 Run Code Coverage Test"
#     s04_public_documentation_website = "04 - 📔 Publish Documentation Website"
#     s05_publish_lambda_layer_version_to_devops = "05 - 🏗️ Publish Lambda Layer Version to 🖥️ devops"
#     s06_deploy_lambda_app_via_cdk_to_sbx_123 = "06 - 🚀 Deploy Lambda App via CDK to 📦 sbx-123"
#     s07_run_integration_test_in_sbx_123 = "07 - 🧪 Run Integration Test in 📦 sbx-123"
#     s08_deploy_lambda_app_via_cdk_to_sbx = "08 - 🚀 Deploy Lambda App via CDK to 📦 sbx"
#     s09_run_integration_test_in_sbx = "09 - 🧪 Run Integration Test in 📦 sbx"
#     s10_deploy_lambda_app_via_cdk_to_tst = "10 - 🚀 Deploy Lambda App via CDK to 🧪 tst"
#     s11_run_integration_test_in_test = "11 - 🧪 Run Integration Test in 🧪 tst"
#     s12_deploy_lambda_app_via_cdk_to_prd = "12 - 🚀 Deploy Lambda App via CDK to 🏭 prd"
#     s13_run_integration_test_in_prd = "13 - 🧪 Run Integration Test in 🏭 prd"
#     s14_create_config_snapshot = "🔯 Create Config Snapshot"
#     s15_create_git_tag = "15 🏷️ Create Git Tag"
#     s16_delete_lambda_app_in_sbx_123 = "16 - 🗑 Delete Lambda App in 📦 sbx-123"
#     s17_delete_lambda_app_in_sbx = "17 - 🗑 Delete Lambda App in 📦 sbx"
#     s18_delete_lambda_app_in_tst = "18 - 🗑 Delete Lambda App in 🧪 tst"
#     s19_delete_lambda_app_in_prd = "19 - 🗑 Delete Lambda App in 🏭 prd"
#     # fmt: on
#
#
# def do_we_run_unit_test(
#     is_ci_runtime: bool,
#     branch_name: str,
#     is_main_branch: bool,
#     is_feature_branch: bool,
#     is_fix_branch: bool,
#     is_layer_branch: bool,
#     is_lambda_branch: bool,
#     is_release_branch: bool,
# ) -> bool:
#     """
#     Check if we should run unit test or coverage test.
#     """
#     if is_ci_runtime:
#         return only_execute_on_certain_branch(
#             branch_name=branch_name,
#             flag_and_branches=[
#                 (is_main_branch, SemanticBranchEnum.main),
#                 (is_feature_branch, SemanticBranchEnum.feature),
#                 (is_fix_branch, SemanticBranchEnum.fix),
#                 (is_layer_branch, AwsOpsSemanticBranchEnum.layer),
#                 (is_lambda_branch, AwsOpsSemanticBranchEnum.awslambda),
#                 (is_release_branch, SemanticBranchEnum.release),
#             ],
#             action=StepEnum.s03_run_code_coverage_test,
#             verbose=True,
#         )
#     # always run unit test on Local
#     else:
#         return True
#
#
# def do_we_deploy_doc(
#     is_ci_runtime: bool,
#     branch_name: str,
#     is_doc_branch: bool,
# ) -> bool:
#     """
#     This function defines the rule for whether we should deploy the
#     documentation website or not.
#     """
#     return simple_python.do_we_deploy_doc(
#         is_ci_runtime=is_ci_runtime,
#         branch_name=branch_name,
#         is_doc_branch=is_doc_branch,
#         _action=StepEnum.s04_public_documentation_website,
#     )
#
#
# def do_we_deploy_lambda_layer(
#     is_ci_runtime: bool,
#     branch_name: str,
#     is_layer_branch: bool,
# ) -> bool:
#     """
#     This function defines the rule for whether we should deploy the
#     Lambda layer or not.
#     """
#     # in CI, we only build layer from layer branch
#     if is_ci_runtime:
#         return only_execute_on_certain_branch(
#             branch_name=branch_name,
#             flag_and_branches=[(is_layer_branch, AwsOpsSemanticBranchEnum.layer)],
#             action=StepEnum.s05_publish_lambda_layer_version_to_devops,
#             verbose=True,
#         )
#     # always allow build layer on local
#     else:
#         return True
#
#
# def do_we_deploy_app(
#     env_name: str,
#     prod_env_name: str,
#     is_local_runtime: bool,
#     branch_name: str,
#     is_main_branch: bool,
#     is_lambda_branch: bool,
#     is_release_branch: bool,
# ) -> bool:
#     """
#     This function defines the rule for whether we should deploy the
#     Lambda app via CDK or not.
#     """
#     flag_and_branches = [
#         (is_main_branch, SemanticBranchEnum.main),
#         (is_lambda_branch, AwsOpsSemanticBranchEnum.awslambda),
#         (is_release_branch, SemanticBranchEnum.release),
#     ]
#     action = "🚀 Deploy Lambda App via CDK"
#     flag = only_execute_on_certain_branch(
#         branch_name=branch_name,
#         flag_and_branches=flag_and_branches,
#         action=action,
#         verbose=True,
#     )
#     if env_name == prod_env_name:
#         if is_local_runtime:
#             return confirm_to_proceed_in_prod(
#                 prod_env_name=prod_env_name,
#                 action=action,
#                 verbose=True,
#             )
#     return flag
#
#
# def do_we_run_int_test(
#     env_name: str,
#     prod_env_name: str,
#     is_ci_runtime: bool,
#     branch_name: str,
#     is_main_branch: bool,
#     is_lambda_branch: bool,
#     is_release_branch: bool,
# ) -> bool:
#     """
#     Check if we should run integration test.
#
#     In CI, we only run integration test when it is a branch that deploy the app.
#
#     There's an exception that, we don't run unit test in prod environment
#     because integration test may change the state of the cloud resources,
#     and it should be already thoroughly tested in previous environments.
#     """
#     # never run int test in prod environment
#     if env_name == prod_env_name:
#         log_why_not_run_integration_test_in_prod(
#             env_name=env_name,
#             prod_env_name=prod_env_name,
#             verbose=True,
#         )
#         return False
#
#     # in CI, we only run integration test from main / lambda / release branch.
#     if is_ci_runtime:
#         return only_execute_on_certain_branch(
#             branch_name=branch_name,
#             flag_and_branches=[
#                 (is_main_branch, SemanticBranchEnum.main),
#                 (is_lambda_branch, AwsOpsSemanticBranchEnum.awslambda),
#                 (is_release_branch, SemanticBranchEnum.release),
#             ],
#             action="🧪 Run integration in Non-prd environment",
#         )
#     # always run int test on Local
#     else:
#         return True
#
#
# def do_we_create_config_snapshot(
#     is_local_runtime: bool,
#     runtime_name: str,
# ) -> bool:
#     """
#     This function defines the rule for whether we should create an immutable
#     config snapshot in parameter store or S3 backend.
#     """
#     # we only do this in local runtime
#     return only_execute_on_certain_runtime(
#         runtime_name=runtime_name,
#         flag_and_runtimes=[(is_local_runtime, RunTimeEnum.LOCAL)],
#         action=StepEnum.s14_create_config_snapshot,
#         verbose=True,
#     )
#
#
# def do_we_create_git_tag(
#     env_name: str,
#     prod_env_name: str,
#     is_ci_runtime: bool,
#     branch_name: str,
#     is_release_branch: bool,
# ) -> bool:
#     """
#     This function defines the rule for whether we should create an immutable
#     git Tag after success deployment to prod.
#
#     In CI, we only run unit test when it is a branch that may change the
#     application code.
#     """
#     if is_ci_runtime:
#         # we ONLY create git tag after success deployment to prod
#         if env_name != prod_env_name:
#             log_why_not_create_git_tag_in_non_prod(
#                 env_name=env_name,
#                 prod_env_name=prod_env_name,
#                 verbose=True,
#             )
#             return False
#
#         return only_execute_on_certain_branch(
#             branch_name=branch_name,
#             flag_and_branches=[(is_release_branch, "release")],
#             action=StepEnum.s15_create_git_tag,
#         )
#     # always don't create git tag on local
#     else:
#         log_why_not_create_git_tag_in_local(
#             env_name=env_name,
#             prod_env_name=prod_env_name,
#             verbose=True,
#         )
#         return False
#
#
# def do_we_delete_app(
#     env_name: str,
#     prod_env_name: str,
#     is_local_runtime: bool,
#     branch_name: str,
#     is_cleanup_branch: bool,
# ) -> bool:
#     """
#     Check if we should delete app.
#     """
#     flag_and_branches = [
#         (is_cleanup_branch, "cleanup"),
#     ]
#     action = "🗑 Delete Lambda App"
#     flag = only_execute_on_certain_branch(
#         branch_name=branch_name,
#         flag_and_branches=flag_and_branches,
#         action=action,
#         verbose=True,
#     )
#     if env_name == prod_env_name:
#         if is_local_runtime:
#             return confirm_to_proceed_in_prod(
#                 prod_env_name=prod_env_name,
#                 action=action,
#                 verbose=True,
#             )
#     return flag
