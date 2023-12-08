# -*- coding: utf-8 -*-

from aws_ops_alpha.rule.simple_lambda.api import (
    rule_set,
    StepEnum,
    GitBranchNameEnum,
    EnvNameEnum,
    RuntimeNameEnum,
)

verbose = False


class TestRuleSet:
    def test_should_we_do_it(self):
        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_LAMBDA_LAYER.value,
            git_branch_name=GitBranchNameEnum.feature.value,
            env_name=EnvNameEnum.sbx.value,
            runtime_name=RuntimeNameEnum.ci.value,
            verbose=verbose,
        )
        assert flag is False

        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_LAMBDA_LAYER.value,
            git_branch_name=GitBranchNameEnum.layer.value,
            env_name=EnvNameEnum.sbx.value,
            runtime_name=RuntimeNameEnum.ci.value,
            verbose=verbose,
        )
        assert flag is False

        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_LAMBDA_LAYER.value,
            git_branch_name=GitBranchNameEnum.layer.value,
            env_name=EnvNameEnum.devops.value,
            runtime_name=RuntimeNameEnum.ci.value,
            verbose=verbose,
        )
        assert flag is True

    def test_display(self):
        rule_set.display(verbose=verbose)


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.rule.rule_set.py", preview=False)
