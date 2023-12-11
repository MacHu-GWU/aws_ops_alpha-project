# -*- coding: utf-8 -*-

import os
import dataclasses
from aws_ops_alpha.boto_ses import AlphaBotoSesFactory, runtime


@dataclasses.dataclass
class BotoSesFactory(AlphaBotoSesFactory):
    def get_env_role_arn(self, env_name: str) -> str:
        aws_account_id = os.environ[f"{env_name.upper()}_AWS_ACCOUNT_ID"]
        return f"arn:aws:iam::{aws_account_id}:role/monorepo_aws-{env_name}-deployer-us-east-1"


boto_ses_factory = BotoSesFactory(
    runtime=runtime,
    env_to_profile_mapper={
        "devops": "bmt_app_devops_us_east_1",
        "sbx": "bmt_app_dev_us_east_1",
        "tst": "bmt_app_test_us_east_1",
        "prd": "bmt_app_prod_us_east_1",
    },
)
bsm = boto_ses_factory.bsm


def test():
    assert boto_ses_factory.get_devops_bsm().aws_account_alias == "bmt-app-devops"
    assert boto_ses_factory.get_env_bsm("sbx").aws_account_alias == "bmt-app-dev"
    assert boto_ses_factory.get_env_bsm("tst").aws_account_alias == "bmt-app-test"
    assert boto_ses_factory.get_env_bsm("prd").aws_account_alias == "bmt-app-prod"


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.boto_ses", preview=False)
