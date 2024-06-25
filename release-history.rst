.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.2.1 (2024-06-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add the following API to allow configuring github settings automatically.
    - ``aws_ops_alpha.bootstrap.github_action.WorkloadAccountBotoSesManagerSetup``
    - ``aws_ops_alpha.bootstrap.github_action.setup_github_repository_settings``
    - ``aws_ops_alpha.bootstrap.github_action.teardown_github_repository_settings``
- Add support for the following project type:
    - ``simple_glue``
    - ``simple_sfn``


0.1.1 (2024-02-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- First usable release
- Add support for the following project type:
    - ``simple_python``
    - ``simple_config``
    - ``simple_cdk``
    - ``simple_lambda``
    - ``simple_lbd_container``
    - ``simple_lbd_agw_chalice``
- Add the following utility tools:
    - ``bootstrap``
    - ``runtime``
    - ``git``
    - ``multi_env``
    - ``boto_ses``
    - ``config``
