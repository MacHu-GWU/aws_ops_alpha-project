aws_ops_alpha Code Architecture
==============================================================================
本节我们将介绍 aws_ops_alpha 的源代码架构. 我们将按照模块在一个 AWS 项目生命周期内被使用到的先后顺序来介绍, 而不是按照字母顺序排列.


``aws_ops_alpha/bootstrap`` Folder
------------------------------------------------------------------------------
在我们为一个新的 AWS 项目创建一个新的 Git Repo 时, 我们需要为该项目在 DevOps 和 Workload Account 中创建所需的用于 DevOps 的资源. 例如负责权限的 IAM Role, 用于存放 Artifacts 的 S3 Bucket, 用于储存 Container Image 的 ECR Repositories 等. :mod:`aws_ops_alpha.bootstrap` 这个模块可以根据你所使用的 CI 工具, 例如 GitHub Action, AWS CodeBuild, CircleCI, Jenkins 等, 创建对应的 AWS 资源.

``bootstrap`` 目录下有以下几个子模块:

- :mod:`aws_ops_alpha.bootstrap.github_action.task`: 用于创建 GitHub Action 所需的 AWS 资源. 主要是 GitHub Action 需要的 Open ID Connect Identity Provider 和 IAM Role.
- :mod:`aws_ops_alpha.bootstrap.multi_account.task`: 用于创建 Multi Workload AWS Accounts 所需的 AWS 资源. 主要是 Cross Account IAM Role, Cross Account S3 Access for Deployment Artifacts.


``aws_ops_alpha/multi_env`` Folder
------------------------------------------------------------------------------
在不同的企业中可能会有不同的 Multi Workload AWS Accounts Setup. 例如有的企业有 ``sandbox``, ``test``, ``production`` 三个. 有的企业有 ``sandbox``, ``test``, ``staging``, ``production`` 四个. :mod:`aws_ops_alpha.multi_env.impl` 模块提供了一些工具能让开发者根据自己企业的需求来创建对应的 Multi Workload AWS Accounts Setup. 具体使用方法请参考 :ref:`multi-environment-deployment-cn`.


``aws_ops_alpha/git`` Folder
------------------------------------------------------------------------------
在 :ref:`semantic-git-branching-cn` 一文中我们介绍了 Semantic Git Branching 的概念. 在不同的企业和项目中我们会有不同的 branching 偏好. :mod:`aws_ops_alpha.git.impl` 模块提供了一些工具能让开发者根据自己的需求来创建对应的 branching 的定义.


``aws_ops_alpha/runtime`` Folder
------------------------------------------------------------------------------
在 :ref:`code-runtime-cn` 一文中我们介绍了 Code Runtime 的概念. 在不同的企业和项目中我们对于 Runtime 的检测方法可能略有不同. :mod:`aws_ops_alpha.runtime.impl` 模块了提供了开箱即用的 runtime 检测工具, 也能让开发者根据自己的需求来创建对应的 runtime 检测逻辑.


``aws_ops_alpha/rule_set.py`` Module
------------------------------------------------------------------------------
在 :ref:`rule-set-cn` 一文中我们介绍了 Conditional Step 和 Rule Set 的概念. 在不同的企业和项目中我们的 Rule Set 也不同. :mod:`aws_ops_alpha.rule_set` 模块提供了一些工具能让开发者根据自己的需求来创建对应的 Rule Set. 并且 ``aws_ops_alpha`` 项目为常见的 AWS 项目提供了一些默认的 Rule Set. 如果你希望自己定义自己的 Rule Set, 请参考 :mod:`aws_ops_alpha.project.simple_python.gen_code` 模块中的注释, 按照以下步骤来维护你的 Rule Set Truth Table 以及你的 Rule Set Python Module:

1. Define enum of ``conditions`` (dimension of the truth table).
2. Generate the initial truth table.
3. Manually update the truth table data.
4. Generate the ``${project_name}_truth_table.py`` Python module.


``aws_ops_alpha/aws_helpers`` Folder
------------------------------------------------------------------------------
AWS Ops 本质上是一步步的 Step 的排列组合. 而在具体项目中根据我们的 Semantic Branching 的设置,


:mod:`aws_ops_alpha.aws_helpers` 模块负责的是




``aws_ops_alpha/boto_ses`` Folder
------------------------------------------------------------------------------

``aws_ops_alpha/config`` Folder
------------------------------------------------------------------------------

``aws_ops_alpha/env_var.py`` Module
------------------------------------------------------------------------------

``aws_ops_alpha/logger.py`` Module
------------------------------------------------------------------------------


