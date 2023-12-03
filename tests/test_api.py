# -*- coding: utf-8 -*-

from aws_ops_alpha import api


def test():
    _ = api
    _ = api.Config
    _ = api.Runtime
    _ = api.RunTimeEnum
    _ = api.runtime
    _ = api.get_devops_aws_account_id_in_ci
    _ = api.get_workload_aws_account_id_in_ci
    _ = api.BotoSesFactory
    _ = api.only_execute_on_certain_runtime
    _ = api.only_execute_on_certain_branch
    _ = api.only_execute_on_certain_env
    _ = api.log_why_not_run_integration_test_in_prod
    _ = api.confirm_to_proceed_in_prod
    _ = api.only_execute_on_certain_runtime_branch_env
    _ = api.log_why_not_create_git_tag_in_non_prod
    _ = api.log_why_not_create_git_tag_in_local
    _ = api.logger
    _ = api.Emoji
    _ = api.constants
    _ = api.simple_lambda


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.api", preview=False)
