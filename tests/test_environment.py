# -*- coding: utf-8 -*-

import os
import pytest

from aws_ops_alpha.runtime import runtime
from aws_ops_alpha.constants import EnvVarNameEnum
from aws_ops_alpha.environment import BaseEnvNameEnum, EnvNameEnum, detect_current_env


class TestEnvEnum:
    def test_emoji(self):
        for env_name in EnvNameEnum:
            _ = env_name.emoji
            # print(f"{env_name = } = {env_name.emoji = }")

    def test_validate(self):
        EnvNameEnum.validate()

        class Enum1(BaseEnvNameEnum):
            devops = "devops"

        with pytest.raises(ValueError):
            Enum1.validate()

        class Enum2(BaseEnvNameEnum):
            dev = "dev"

        with pytest.raises(ValueError):
            Enum2.validate()


class MyEnvNameEnum(BaseEnvNameEnum):
    devops = "devops"
    sbx = "sbx"
    prd = "prd"


class TestMyEnvEnum:
    def test(self):
        os.environ[EnvVarNameEnum.USER_ENV_NAME.value] = "sbx"
        env_name = detect_current_env(runtime, MyEnvNameEnum)
        # print(f"{env_name = }")


def test_detect_current_env():
    os.environ[EnvVarNameEnum.USER_ENV_NAME.value] = "sbx"
    env_name = detect_current_env(runtime, MyEnvNameEnum)
    # print(f"{env_name = }")


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.environment", preview=False)
