aws_ops_alpha Code Architecture (CN)
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


``aws_ops_alpha/boto_ses`` Folder
------------------------------------------------------------------------------
既然是 AWS 项目, 那么就必然涉及到 boto session 的创建以及管理.

:mod:`aws_ops_alpha.boto_ses.impl` 模块提供了一些工具, 能让开发者根据自己的需求管理所有用到的 boto session, 主要是 1 个 devops session 和 N 个 workload session. 下面我们给出了一个使用 ``aws_ops_alpha.boto_ses`` 模块对项目中的 AWS boto session 进行管理的例子.

.. dropdown:: Sample boto_ses.py

    .. code-block:: python

        # content of boto_ses.py
        # -*- coding: utf-8 -*-

        """
        Define the boto session creation setup for this project.
        """

        import os
        import dataclasses
        from functools import cached_property

        from s3pathlib import context

        from .vendor.import_agent import aws_ops_alpha

        from .env import EnvNameEnum, detect_current_env
        from .runtime import runtime


        @dataclasses.dataclass
        class BotoSesFactory(aws_ops_alpha.AlphaBotoSesFactory):
            def get_env_role_arn(self, env_name: str) -> str:  # pragma: no cover
                aws_account_id = os.environ[f"{env_name.upper()}_AWS_ACCOUNT_ID"]
                return f"arn:aws:iam::{aws_account_id}:role/monorepo_aws-{env_name}-deployer-us-east-1"

            def get_env_role_session_name(self, env_name: str) -> str: # pragma: no cover
                return f"{env_name}_role_session"

            def get_current_env(self) -> str:
                return detect_current_env()

            @cached_property
            def bsm_sbx(self):
                return self.get_env_bsm(env_name=EnvNameEnum.sbx.value)

            @cached_property
            def bsm_tst(self):
                return self.get_env_bsm(env_name=EnvNameEnum.tst.value)

            # @cached_property
            # def bsm_stg(self):
            #     return self.get_env_bsm(env_name=EnvEnum.stg.value)

            @cached_property
            def bsm_prd(self):
                return self.get_env_bsm(env_name=EnvNameEnum.prd.value)

            @cached_property
            def workload_bsm_list(self):
                return [
                    self.bsm_sbx,
                    self.bsm_tst,
                    # self.bsm_stg,
                    self.bsm_prd,
                ]

            def print_who_am_i(self):  # pragma: no cover
                masked = not runtime.is_local_runtime_group
                for name, bsm in [
                    ("bsm_devops", boto_ses_factory.bsm_devops),
                    ("bsm_sbx", boto_ses_factory.bsm_sbx),
                    ("bsm_tst", boto_ses_factory.bsm_tst),
                    # ("bsm_stg", boto_ses_factory.bsm_tst),
                    ("bsm_prd", boto_ses_factory.bsm_prd),
                ]:
                    print(f"--- {name} ---")
                    bsm.print_who_am_i(masked=masked)


        boto_ses_factory = BotoSesFactory(
            runtime=runtime,
            env_to_profile_mapper={
                EnvNameEnum.devops.value: "devops_profile",
                EnvNameEnum.sbx.value: "dev_profile",
                EnvNameEnum.tst.value: "test_profile",
                # EnvEnum.stg.value: "stg_profile",
                EnvNameEnum.prd.value: "prod_profile",
            },
            default_app_env_name=EnvNameEnum.sbx.value,
        )

        bsm = boto_ses_factory.bsm

        # Set default s3pathlib boto session
        context.attach_boto_session(boto_ses=bsm.boto_ses)


``aws_ops_alpha/config`` Folder
------------------------------------------------------------------------------
由于生产项目会有多个 Environment. 所以就需要一个配置管理系统来对属于不同的 Environment 进行管理. :mod:`aws_ops_alpha.config` 模块提供了一整套工具能让开发者为具体项目轻松的创建 Config 管理模块, 自动化 Config 的编写, 修改, 部署, 测试以及使用.


``aws_ops_alpha/env_var.py`` Module
------------------------------------------------------------------------------
在 DevOps 中使用环境变量是一个非常重要的技巧. 对于 AWS 项目, 我们定义了一些默认的环境变量用于存储一些关键信息. 这个模块提供了一些函数能让开发者方便地管理这些信息. 例如我们用 ``${ENV_NAME}_AWS_ACCOUNT_ID`` 这个环境变量储存 AWS Account Id 的信息. 详情请查阅 :mod:`aws_ops_alpha.env_var` 的源代码.


``aws_ops_alpha/logger.py`` Module
------------------------------------------------------------------------------
这是一个用来在 DevOps automation script 中打日志的模块.


``aws_ops_alpha/aws_helpers`` Folder
------------------------------------------------------------------------------
AWS Ops 本质上是一步步的 Step 的排列组合. 而在具体项目中 Step 需要根据我们的 env_name, runtime, semantic_branch_name 的排列组合决定是不是要运行.

:mod:`aws_ops_alpha.aws_helpers` 模块则抛开 Condition 相关的逻辑, 假设我们就是要执行这些 Step, 然后把这些 Step 的业务逻辑封装成函数. 这样可以实现具体的 Step 逻辑和 Condition 逻辑解耦合.


``aws_ops_alpha/project`` Folder
------------------------------------------------------------------------------
这个模块是 AWS Ops 的核心, 它把 ``rule_set`` 中的 Condition 规则, 和 ``aws_helpers`` 中的 Step 逻辑结合起来, 封装成了函数, 并且加上了一些 logging. 相当于是为每一个 Step 创建了一个函数, 它能自动判断要不要 Run, 然后在 Run 的过程中自动打上日志. 这些函数都是高度参数化的, 开发者可以在实际的项目中 import 它们, 并且传入参数来运行常见的 DevOps Step. 这些参数通常是 boto session, truth table 对象等等. 这样的设计可以大大简化开发者在实际项目中的工作量. 如果开发者使用 ``aws_ops_alpha`` 所推荐的默认设置, 则基本什么都不用改. 而如果开发者使用了自定义的 ``env_name``, ``runtime``, ``semantic_branch_name``, ``rule_set``, 则只需要传入对应的自定义参数即可.


``aws_ops_alpha/project/${project_type}`` Folder
------------------------------------------------------------------------------
对于每一种 project 类型 (比如 cdk 是一种类型的 project, lambda 是另一种类型的 project),

- ``gen_code.py``: 在为一个新的 project 类型定义 Conditional Step 之前, 需要在这个模块中定义有哪些 Step, 哪些 branch, 哪些 runtime, 哪些 env_name. 然后运行这个脚本就会自动生成 ``should_we_do_it.tsv`` 模版供开发者进行编辑. 如果你已经编辑好了 ``should_we_do_it.tsv`` 文件, 运行这个脚本则会自动生成 ``${project_type}_truth_table.py`` 和 ``${project_type}_truth_table.py`` 两个文件.
- ``should_we_do_it.tsv``: 开发者用于本地编辑的文件, 用于定义 Condition 规则. 这个文件不会被 check in 到 Git 中.
- ``${project_type}_truth_table.tsv``: ``should_we_do_it.tsv`` 的副本, 会被 check in 到 Git 中.
- ``${project_type}_truth_table.py``: 一个 Python 模块, 提供了一个简洁的 API 用于读取 ``${project_type}_truth_table.tsv`` 文件中的数据, 并根据 condition 的情况决定 step 要不要被执行. 这个模块会被 ``aws_ops_alpha.project.${project_type}.step.py`` 模块使用.
- ``rule_set.py``: 对 Condition 的 Enum 做一些自定义的处理. 最终会被 ``aws_ops_alpha.project.${project_type}.step.py`` 模块使用.
- ``step.py``: 定义了在这种 project 类型中会用到的 Step 的自动化脚本的函数. 这些函数通常会打上一些 Log.

这里我们重点说一下 ``step.py`` 模块. 这个模块定义了 DevOps Step 的核心逻辑, 也是这个库最主要的 Public API.

从代码设计的角度看, 一个 DevOps Step 包含几块内容:

1. Step Logic, 核心业务逻辑, 比如构建依赖, 部署代码. 这部分逻辑一般是用 Python 函数或是 subprocess 实现的.
2. Conditional Step, 在当前的 env_name, runtime, semantic_branch_name 的情况下, 我们要不要运行这个 Step.
3. Logging, 在执行 Step 的过程中打上 Log, 以便于后续的 Debug.

我们一个个来看.

Step Logic 的逻辑很多都在 :mod:`aws_ops_alpha.aws_helpers` 中已经被实现了. 在这里我们主要做的是将这些逻辑的参数重新进行排列组合, 让它更容易被实际项目所使用. 这里面常见的参数包括 env_name, bsm_devops, bsm_workload, s3dir_artifacts 等.

Conditional Step 的判定逻辑主要由前面的 :mod:`aws_ops_alpha.rule_set` 实现. 在这里我们主要是将 ``rule_set.py`` 和 ``${project_type}_truth_table.py`` 中的功能 import 进来, 然后进行判断. 所以这里的每个 Step 函数你通常会看到 ``env_name``, ``runtime_name``, ``semantic_branch_name`` 以及 ``check``, ``step``, ``truth_table``, ``url`` 这些跟 Conditional Step 相关的参数. 这里有必要重点说一下 ``step`` 这个参数. 这个参数是 step 的名字. 我们拿一个具体场景作为例子. 出于代码复用的目的, 我们在 ``simple_cdk`` project type 的 Step 里实现了 cdk deploy 的逻辑. 在 ``simple_cdk`` 项目中, 这个 step 叫 ``deploy_cdk_stack``. 而在 ``simple_lambda`` project type 的 Step 里我们有一步是 deploy lambda app via CDK. 本质上这一步还是在做 cdk deploy, 并且在 truth table 中这一步也是 ``deploy_cdk_stack``, 虽然这个项目是 ``simple_lambda``, 但这个 step 还是叫 ``deploy_cdk_stack``.

Logging 主要是在执行某一个动作之前打上日志, 告诉用户我要做什么了. 然后根据执行的结果, 是成功还是失败, 有哪些用户需要知道的信息, 把这些信息打到日志上. 因为所有的 logging 都是由一个叫 logger 的对象来实现的, 所以我们可以用 ``logger.disable()`` context manager 在任何地方临时禁用 logging (例如在单元测试时我们不需要打 log, 不然 test output 会很乱).


``aws_ops_alpha/project/simple_python`` Folder
------------------------------------------------------------------------------


``aws_ops_alpha/project/simple_config`` Folder
------------------------------------------------------------------------------


``aws_ops_alpha/project/simple_cdk`` Folder
------------------------------------------------------------------------------


``aws_ops_alpha/project/simple_lambda`` Folder
------------------------------------------------------------------------------


``aws_ops_alpha/project/simple_lbd_container`` Folder
------------------------------------------------------------------------------


``aws_ops_alpha/project/simple_lbd_agw_chalice`` Folder
------------------------------------------------------------------------------


``aws_ops_alpha/project/simple_glue`` Folder
------------------------------------------------------------------------------


``aws_ops_alpha/project/simple_sfn`` Folder
------------------------------------------------------------------------------
