# -*- coding: utf-8 -*-

from ...vendor import semantic_branch as sem_branch
from ...rule_set import should_we_do_it as _should_we_do_it

from .simple_cdk_truth_table import SemanticBranchNameEnum, truth_table

semantic_branch_rules = {
    SemanticBranchNameEnum.main: ["main", "master"],
    SemanticBranchNameEnum.feature: ["feature", "feat"],
    SemanticBranchNameEnum.fix: ["fix"],
    SemanticBranchNameEnum.doc: ["doc"],
    SemanticBranchNameEnum.app: ["app"],
    SemanticBranchNameEnum.release: ["release", "rls"],
    SemanticBranchNameEnum.cleanup: ["cleanup", "clean"],
}

semantic_branch_rule = sem_branch.SemanticBranchRule(
    rules=semantic_branch_rules,
)

google_sheet_url = "https://docs.google.com/spreadsheets/d/1OI3GXTUBtAbMyaLSnh_1S1X0jfTCBaFPIJLeRoP_uAY/edit#gid=58120413"


def should_we_do_it(
    step: str,
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
) -> bool:
    return _should_we_do_it(
        step=step,
        semantic_branch_name=semantic_branch_name,
        runtime_name=runtime_name,
        env_name=env_name,
        truth_table=truth_table,
        google_sheet_url="https://docs.google.com/spreadsheets/d/1OI3GXTUBtAbMyaLSnh_1S1X0jfTCBaFPIJLeRoP_uAY/edit#gid=58120413",
    )
