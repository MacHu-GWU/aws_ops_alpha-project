# -*- coding: utf-8 -*-

from aws_ops_alpha import api


def test():
    _ = api
    _ = api.AwsOpsAlphaConfig
    _ = api.Runtime
    _ = api.RunTimeEnum
    _ = api.runtime
    _ = api.get_devops_aws_account_id_in_ci
    _ = api.get_workload_aws_account_id_in_ci
    _ = api.temp_env_var
    _ = api.EnvEnum
    _ = api.detect_current_env
    _ = api.GitRepo
    _ = api.MultiGitRepo
    _ = api.MonoGitRepo
    _ = api.BotoSesFactory
    _ = api.logger
    _ = api.constants
    _ = api.aws_cdk_helpers
    _ = api.aws_lambda_helpers
    _ = api.simple_python_project
    _ = api.simple_cdk_project
    _ = api.simple_lambda_project


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.api", preview=False)
