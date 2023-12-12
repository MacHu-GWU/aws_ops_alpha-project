# -*- coding: utf-8 -*-

import os

import pytest

from aws_ops_alpha.constants import USER_ENV_NAME
from aws_ops_alpha.runtime import runtime
from aws_ops_alpha.environment import BaseWorkloadEnvEnum, EnvEnum, detect_current_env


class MyEnvEnum(BaseWorkloadEnvEnum):
    sbx = "sbx"
    prd = "prd"


class TestEnvEnum:
    def test_emoji(self):
        for env_name in EnvEnum:
            _ = env_name.emoji
            # print(f"{env_name = } = {env_name.emoji = }")

    def test_validate(self):
        EnvEnum.validate()

        class Enum1(BaseWorkloadEnvEnum):
            devops = "devops"

        with pytest.raises(ValueError):
            Enum1.validate()

        class Enum2(BaseWorkloadEnvEnum):
            dev = "dev"

        with pytest.raises(ValueError):
            Enum2.validate()


class TestMyEnvEnum:
    def test(self):
        env_name = detect_current_env(runtime, MyEnvEnum)
        # print(f"{env_name = }")


def test_detect_current_env():
    env_name = detect_current_env(runtime, EnvEnum)
    # print(f"{env_name = }")


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.environment", preview=False)
