# -*- coding: utf-8 -*-

from aws_ops_alpha.runtime import runtime
from aws_ops_alpha.environment import EnvEnum, detect_current_env


class TestEnvEnum:
    def test_emoji(self):
        for env_name in EnvEnum:
            _ = env_name.emoji


def test():
    _ = detect_current_env(runtime)


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.environment", preview=False)
