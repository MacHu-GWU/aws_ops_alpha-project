# -*- coding: utf-8 -*-

import pytest
import typing as T
import dataclasses
from functools import cached_property

from aws_ops_alpha.constants import CommonEnvNameEnum
from aws_ops_alpha.paths import dir_project_root
from aws_ops_alpha.runtime import runtime
from aws_ops_alpha.environment import BaseEnvNameEnum, detect_current_env
from aws_ops_alpha.boto_ses import AlphaBotoSesFactory
from aws_ops_alpha.config.api import Config, Env, load_config


class MyEnvNameEnum(BaseEnvNameEnum):
    devops = "devops"
    sbx = "sbx"
    prd = "prd"


@dataclasses.dataclass
class MyEnv(Env):
    username: T.Optional[str] = dataclasses.field(default=None)
    password: T.Optional[str] = dataclasses.field(default=None)


@dataclasses.dataclass
class MyConfig(Config):
    @classmethod
    def get_current_env(cls) -> str:  # pragma: no cover
        raise detect_current_env(runtime, MyEnvNameEnum)

    @cached_property
    def sbx(self) -> Env:  # pragma: no cover
        return self.get_env(env_name=MyEnvNameEnum.sbx)

    @cached_property
    def prd(self) -> Env:  # pragma: no cover
        return self.get_env(env_name=MyEnvNameEnum.prd)


@dataclasses.dataclass
class BotoSesFactory(AlphaBotoSesFactory):
    def get_env_role_arn(self, env_name: str) -> str:
        return ""

boto_ses_factory = BotoSesFactory(
    runtime=runtime,
    env_to_profile_mapper={
        MyEnvNameEnum.devops.value: "bmt_app_devops_us_east_1",
        MyEnvNameEnum.sbx.value: "bmt_app_dev_us_east_1",
        MyEnvNameEnum.prd.value: "bmt_app_prod_us_east_1",
    },
    default_app_env_name=MyEnvNameEnum.sbx.value,
)

dir_tests = dir_project_root / "tests"
path_config_json = dir_tests / "test_config.json"
path_config_secret_json = dir_tests / "test_config_secret.json"


skip_test = runtime.is_local is False

@pytest.mark.skipif(skip_test, reason="we don't want to run this test in CI")
def test():
    config = load_config(
        runtime=runtime,
        env_name_enum_class=MyEnvNameEnum,
        config_class=MyConfig,
        env_class=MyEnv,
        path_config_json=path_config_json,
        path_config_secret_json=path_config_secret_json,
        boto_ses_factory=boto_ses_factory,
    )
    from rich import print as rprint
    rprint(config)


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.config", preview=False)
