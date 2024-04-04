# -*- coding: utf-8 -*-

"""
Bootstrap for GitHub Action.
"""

# --- standard library
import typing as T
import dataclasses
from textwrap import dedent

# --- third party library (include vendor)
import aws_cloudformation.api as aws_cf
import gh_action_open_id_in_aws.api as gh_action_open_id_in_aws

try:
    from github import (
        Github,
        EnvironmentProtectionRuleReviewer,
        EnvironmentDeploymentBranchPolicy,
    )
except ImportError:  # github related automation is optional
    pass

# --- modules from this project
from ...constants import AwsTagNameEnum

# --- modules from this submodule

# --- type hint
if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager


def setup_github_action_open_id_connection(
    bsm_devops: "BotoSesManager",
    stack_name: str,
    github_org: str,
    github_repo: str,
    gh_action_role_name: str,
    oidc_provider_arn: str = "",
):
    """
    The OpenID Connect (OIDC) identity provider that allows the GitHub Actions
    to assume the role in the DevOps account.

    :param bsm_devops: the boto3 session manager for the DevOps account
    :param stack_name: the cloudformation stack name to set up the OpenID Connect
    :param github_org: the GitHub organization name trusted by the IAM role
    :param github_repo: the GitHub repository name trusted by the IAM role,
        could be "*"
    :param gh_action_role_name: the IAM role name to be assumed by the GitHub Actions
    :param oidc_provider_arn: the OIDC provider arn, if not provided, it will
        create a new OIDC provider. if provided, reuse the existing one.
        leave it empty if it is the first time to set up the OIDC provider in
        the given AWS account.
    """
    with bsm_devops.awscli():
        gh_action_open_id_in_aws.setup_github_action_open_id_connection_in_aws(
            aws_profile=None,
            stack_name=stack_name,
            github_org=github_org,
            github_repo=github_repo,
            role_name=gh_action_role_name,
            oidc_provider_arn=oidc_provider_arn,
            tags={
                AwsTagNameEnum.tech_project_name.value: "monorepo_aws",
                AwsTagNameEnum.tech_env_name: "devops sbx tst prd",
                AwsTagNameEnum.tech_description: (
                    "setup Github Action open id connection in AWS "
                    "so that Github Action can assume an IAM role to do deployment"
                ),
            },
        )

    print(
        dedent(
            """
    Note that the created IAM role won't have any permission, you need to configure it yourself. 

    Usually, GitHub action is used for CI/CD, you may need the following permissions to perform common CI/CD tasks:

    1. Manage (Create / Update / Delete) IAM Role / Policy
    2. Manage (Create / Update / Delete) AWS CloudFormation stack.
    3. Manage (Create / Update / Delete) AWS S3 Bucket to read / write deployment artifacts.
    4. Manage (Create / Update / Delete) AWS Parameter Store to read and write parameters.
    5. Manage (Create / Update / Delete) AWS ECR to push and pull container images and share it to workload AWS accounts.
    6. Manage (Create / Update / Delete) AWS EC2 AMI and share it to workload AWS accounts.
    7. Manage (Create / Update / Delete) AWS SNS Topic to send notifications.
    """
        )
    )


def teardown_github_action_open_id_connection(
    bsm_devops: "BotoSesManager",
    stack_name: str,
):
    """
    Remove the OpenID Connect (OIDC) identity provider that allows the GitHub Actions
    to assume the role in the DevOps account.

    :param bsm_devops: the boto3 session manager for the DevOps account
    :param stack_name: the cloudformation stack name to set up the OpenID Connect
    """
    aws_cf.remove_stack(
        bsm=bsm_devops,
        stack_name=stack_name,
        skip_prompt=False,
    )


@dataclasses.dataclass
class WorkloadAccountBotoSesManagerSetup:
    bsm: "BotoSesManager"
    env_name: str


def setup_github_repository_settings(
    pac: str,
    github_org: str,
    github_repo: str,
    bsm_devops: "BotoSesManager",
    workload_account_bsm_setup_list: T.List["WorkloadAccountBotoSesManagerSetup"],
):  # pragma: no cover
    """
    Set the GitHub repository settings, including:

    - Create necessary repository secrets. We need the AWS Account id for each environment.
    - Create deployment environment configuration. We need to manual approve the deployment
        in the production environment.

    Ref:

    - https://docs.github.com/en/rest/actions/secrets?apiVersion=2022-11-28#create-or-update-a-repository-secret
    - https://docs.github.com/en/rest/deployments/environments?apiVersion=2022-11-28#create-or-update-an-environment

    :param pac: the GitHub personal access token that has the necessary permission
    :param github_org: the GitHub organization name trusted by the IAM role
    :param github_repo: the GitHub repository name trusted by the IAM role,
    :param bsm_devops: the boto3 session manager for the DevOps account
    :param workload_account_bsm_setup_list: list of
        :class`WorkloadAccountBotoSesManagerSetup` objects.
    """
    gh = Github(pac)
    github_user_id = gh.get_user().id  # this user id will be used in deployment review
    repo = gh.get_repo(f"{github_org}/{github_repo}")
    repo.create_secret(
        secret_name="DEVOPS_AWS_ACCOUNT_ID",
        unencrypted_value=bsm_devops.aws_account_id,
        secret_type="actions",
    )

    for workload_account_bsm_setup in workload_account_bsm_setup_list:
        # create repository secret
        repo.create_secret(
            secret_name=f"{workload_account_bsm_setup.env_name.upper()}_AWS_ACCOUNT_ID",
            unencrypted_value=workload_account_bsm_setup.bsm.aws_account_id,
            secret_type="actions",
        )
        # create deployment environment
        kwargs = dict(environment_name=workload_account_bsm_setup.env_name)
        # only allow the reviewer in the production environment
        if workload_account_bsm_setup.env_name == "prd":
            kwargs["reviewers"] = [
                EnvironmentProtectionRuleReviewer.ReviewerParams(
                    type_="User",
                    id_=github_user_id,
                ),
            ]
        repo.create_environment(**kwargs)

    print(
        dedent(
            f"""
    You can verify the settings in the GitHub repository settings page:

    - Repository secrets: https://github.com/{github_org}/{github_repo}/settings/secrets/actions
    - Deployment environments: https://github.com/{github_org}/{github_repo}/settings/environments
    """
        )
    )


def teardown_github_repository_settings(
    pac: str,
    github_org: str,
    github_repo: str,
    workload_env_list: T.List[str],
):  # pragma: no cover
    """
    Teardown the setup defined in :func:`setup_github_repository_settings`.

    :param pac: the GitHub personal access token that has the necessary permission
    :param github_org: the GitHub organization name trusted by the IAM role
    :param github_repo: the GitHub repository name trusted by the IAM role,
    :param workload_env_list: list of workload environment name. For example:
        ``["sbx", "tst", "prd"]``.
    """
    gh = Github(pac)
    repo = gh.get_repo(f"{github_org}/{github_repo}")
    secret_list = repo.get_secrets(
        secret_type="actions",
    )
    secret_name_list = [secret.name for secret in secret_list]
    for env_name in [f"DEVOPS_AWS_ACCOUNT_ID"] + [
        f"{env_name.upper()}_AWS_ACCOUNT_ID" for env_name in workload_env_list
    ]:
        if env_name in secret_name_list:
            repo.delete_secret(secret_name=env_name)

    environment_list = repo.get_environments()
    environment_name_list = [environment.name for environment in environment_list]
    for env_name in workload_env_list:
        if env_name in environment_name_list:
            repo.delete_environment(environment_name=env_name)
