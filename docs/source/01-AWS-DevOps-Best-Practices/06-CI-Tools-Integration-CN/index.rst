.. _ci-tools-integration-cn:

CI Tools Integration (CN)
==============================================================================


.. _ci-agnostic-integration:

CI Agnostic Integration
------------------------------------------------------------------------------
市场上有非常多的 CI 工具可供选择. 当我们选择把我们的 DevOps 代码集成到 CI 工具中时, 有以下因素可能会成为我们的挑战.我们可能会遇到以下问题

1. 在大企业的中, 不同的项目组也可能会使用不同的 CI 工具, 这使得 DevOps 的工作在不同的项目组中不通用, 需要为每一个项目维护一套专用的工具.
2. 有的企业的核心工作是外包公司, 在不同的客户项目中, 也可能会使用不同的 CI 工具. 也就会出现跟 #1 一样的问题.
3. 有的项目的声明周期很长, 可能会因为某种非技术性原因替换 CI 工具. 这使得项目的 Migration 变得非常困难.
4. 对于开发者个人而言, 职业生涯中可能会接触到使用不同 CI 工具的不同项目. 而如果每个项目中学到的经验在其他项目中都不通用, 这将会大大浪费职业成长的时间.

综上, 在理想情况下, 我们做项目时将 DevOps 代码集成到 CI 工具中的方式应该是通用的, 应该避免强依赖于 CI 工具中的特定功能. 这样我们的 DevOps 代码才能在不同的项目中通用, 也才能在不同的 CI 工具中通用. 例如在我们的 DevOps 中有一个对 Deployment 的 Name 的字符串处理逻辑, 我们在 Jenkins 中应该避免在 Groovy 中做这个处理, 在 GitHub Action 中也不应该用 String Interpolation 来做这个处理, 而是应该交给我们自己的 Shell Script 来做.


Multiple Deployment Orchestration
------------------------------------------------------------------------------
在 :ref:`tricks-deploy-multiple-project-together-in-monorepo` 一文中, 我们介绍了将大项目分拆成独立的 Deployment Unit 的好处. 也介绍了如何将多个 DU 打包部署的通用方法. 但是这个方法在不同的 CI 中的实现方式可能会有所不同.


GitHub CI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
在 GitHub Action 中, `Step <https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idsteps>`_ 是对 Terminal Command 的封装. 我们可以用 GitHub Action Step 来编排我们的 DevOps Step.

GitHub Action 有 `Reusing Workflow <https://docs.github.com/en/actions/using-workflows/reusing-workflows>`_ 功能. 你可以在一个 Workflow 中并行或者串行运行其他的 Workflow. 虽然它有最多 Nest 4 层的限制, 但是对于大部分应用场景来说已经足够了.


CodeBuild + CodePipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
在 AWS CodeBuild 中, `Commands <https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-syntax>`_ 是对 Terminal Command 的封装, 我们可以用 Commands 来编排我们的 DevOps Step.

在 AWS CodePipeline 中, `Build Stage <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html>`_ 可以用来并行或串行运行多个 AWS CodeBuild Job Run, 甚至是多个 AWS CodePipeline. 这样我们就可以将多个 DU 打包运行了.


CircleCI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
在 CirCleCI 中, `Steps <https://circleci.com/docs/jobs-steps/#steps-overview>`_ 是对 Terminal Command 的封装. 我们可以用 CircleCI Step 来编排我们的 DevOps Step.

在 CircleCI 中, 你可以用 Workflow + Jobs 来部署多个 DU. 目前 (2024-01-01) 没发现 CircleCI 能在 Job 中运行其他的 YAML Workflow. 所以我们可能要将 DU 的 YAML 代码拷贝到新的 Workflow 中去.


GitLab CI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
todo


BitBucket Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
todo


Jenkins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
todo


Shell Script in Python
------------------------------------------------------------------------------
在 DevOps 的社区中, 最流行的脚本工具是 bash script. 我们推荐在新项目中将所有的 bash script 替换成 Python script. 理由如下:

1. Bash 不是一个通用的, 图灵完备的编程语言. 在 Bash 中做流程控制, 字符串处理, 数据结构, 函数复用等都很困难. 而 Python 是一个通用编程语言, 并且社区有很多库能帮助我们轻松做到很多事情. 在 Python 中做流程控制, 字符串处理, 数据结构, 函数复用都很容易.
2. Bash 代码的可读性远远差于 Python.
3. 凡是 Bash 中能运行的命令, Python 中都能用 subprocess, 或是 sys, 或是 os 模块来做到. Python 社区中有一个更强的库 `sh <https://sh.readthedocs.io/en/latest/>`_, 可以是我们在 Python 中写 Command 像 Bash 中一样方便, 但是更可读, 更容易复用.

.. note::

    如果你的项目中已经有很多精心设计过并且能够复用的 Bash Script, 而迁徙到 Python 的成本又很高, 那么你有足够的理由选择不迁徙.

在 :ref:`ci-agnostic-integration` 我们提到了尽量不依赖 CI 系统的特定功能来实现 DevOps 逻辑. 而我们使用很多 CI 系统特定的功能的一个最主要的原因是该功能不容易在 Bash Script 或 Terminal Command 中实现. 而对于 Python 而言, 有什么是困难的呢?
