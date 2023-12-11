# -*- coding: utf-8 -*-

import itertools
from aws_ops_alpha.project.simple_python.rule import rule_set
from aws_ops_alpha.project.simple_python.constants import (
    StepEnum,
    GitBranchNameEnum,
    EnvNameEnum,
    RuntimeNameEnum,
)

verbose = False


class TestRuleSet:
    def test_get_flag(self):
        for git_branch_name, env_name, runtime_name in itertools.product(
            GitBranchNameEnum,
            EnvNameEnum,
            RuntimeNameEnum,
        ):
            for step in StepEnum:
                flag = rule_set.get_flag(
                    step=step,
                    git_branch_name=git_branch_name,
                    env_name=env_name,
                    runtime_name=runtime_name,
                )
                _ = flag

    def test_display(self):
        rule_set.display(verbose=verbose)


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.rule.rule_set.py", preview=False)
