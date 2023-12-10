# -*- coding: utf-8 -*-

import dataclasses
from aws_ops_alpha.boto_ses import AwsOpsAlphaConfig, runtime, BotoSesFactory

aws_ops_alpha_config = AwsOpsAlphaConfig(
    env_aws_profile_mapper={
        "devops": "bmt_app_devops_us_east_1",
        "sbx": "bmt_app_dev_us_east_1",
        "tst": "bmt_app_test_us_east_1",
        "prd": "bmt_app_prod_us_east_1",
    }
)


@dataclasses.dataclass
class BotoSesFactory(BotoSesFactory):
    def get_env_role_name(self, env_name: str) -> str:
        return f"monorepo_aws-{env_name}-deployer-us-east-1"


boto_ses_factory = BotoSesFactory(
    config=aws_ops_alpha_config,
    runtime=runtime,
)
bsm = boto_ses_factory.bsm


def test():
    _ = boto_ses_factory.get_devops_bsm().aws_account_id
    _ = boto_ses_factory.get_app_bsm("sbx").aws_account_id
    _ = boto_ses_factory.get_app_bsm("tst").aws_account_id
    _ = boto_ses_factory.get_app_bsm("prd").aws_account_id


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.boto_ses", preview=False)
