# -*- coding: utf-8 -*-

import aws_ops_alpha.project.simple_glue.api as simple_glue


def test():
    _ = simple_glue.StepEnum
    _ = simple_glue.SemanticBranchNameEnum
    _ = simple_glue.RuntimeNameEnum
    _ = simple_glue.EnvNameEnum
    _ = simple_glue.truth_table
    _ = simple_glue.semantic_branch_rule
    _ = simple_glue.google_sheet_url
    _ = simple_glue.pip_install_awsglue
    _ = simple_glue.build_glue_extra_py_files_artifact
    _ = simple_glue.publish_glue_extra_py_files_artifact_version
    _ = simple_glue.build_glue_script_artifact
    _ = simple_glue.publish_glue_script_artifact_version
    _ = simple_glue.run_glue_unit_test
    _ = simple_glue.run_glue_int_test
    _ = simple_glue.deploy_app
    _ = simple_glue.delete_app


if __name__ == "__main__":
    from aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "aws_ops_alpha.project.simple_glue", preview=False)
