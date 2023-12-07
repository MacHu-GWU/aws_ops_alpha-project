# -*- coding: utf-8 -*-

import enum

from ..vendor.semantic_branch import SemanticBranchEnum


class StepEnum(str, enum.Enum):
    """
    Explains:

    - Publish documentation website from the latest code if needed.
    """

    # fmt: off
    public_documentation_website = "📔 Publish Documentation Website"
    # fmt: on


def do_we_deploy_doc(
    is_ci_runtime: bool,
    branch_name: str,
    is_doc_branch: bool,
    _action: str = StepEnum.public_documentation_website,
) -> bool:
    """
    This function defines the rule for whether we should deploy the
    documentation website or not.
    """
    # in CI, we only deploy documentation website from doc branch
    if is_ci_runtime:
        return only_execute_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[(is_doc_branch, SemanticBranchEnum.doc)],
            action=_action,
            verbose=True,
        )
    # always deploy doc on Local
    else:
        return True
