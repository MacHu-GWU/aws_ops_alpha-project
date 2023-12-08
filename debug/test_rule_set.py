# -*- coding: utf-8 -*-

from aws_ops_alpha.workflow.simple_python.api import (
    StepEnum,
    GitBranchNameEnum,
    EnvNameEnum,
    RuntimeNameEnum,
    rule_set,
)

flag = rule_set.should_we_do_it(
    StepEnum.RUN_CODE_COVERAGE_TEST,
    git_branch_name=GitBranchNameEnum.main,
    env_name=EnvNameEnum.sbx,
    runtime_name=RuntimeNameEnum.local,
)
print(flag)