# -*- coding: utf-8 -*-

from aws_ops_alpha.workflow.simple_lambda.workflow import GitBranchNameEnum, _detect_semantic_branch


def test_detect_semantic_branch():
    assert _detect_semantic_branch("main") == GitBranchNameEnum.main
    assert _detect_semantic_branch("feature") == "main"


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.workflow.simple_lambda.workflow.py", preview=False)
