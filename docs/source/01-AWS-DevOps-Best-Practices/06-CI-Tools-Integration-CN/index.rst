.. _ci-tools-integration-cn:

CI Tools Integration (CN)
==============================================================================
``aws_ops_alpha`` 是一个框架, 一个抽象层. 它不是只为某一个具体的 CI 工具而服务的库, 它的目的是能允许开发者在不同的 CI 工具之间无痛切换. 本节我们主要介绍 ``aws_ops_alpha`` 库做了哪些工作来实现这一点.


Key Problems for CI Tools Integration
------------------------------------------------------------------------------
用不同的 CI 工具来部署 AWS 项目这里有两个难点需要解决.

1. **一次开发, 到处运行**: 市场上的 CI 工具很多, 它们的功能也不一样, 如何将不同的 CI 工具与 aws_ops_alpha 集成起来? 例如 GitHub Action 和 CircleCI 对 CI 代码的复用支持很好, 而 AWS CodeBuild 则没有这一功能. 例如 AWS CodePipeline 支持直接 Deploy CloudFormation 而无需启动一个运行环境, 而其他 CI 工具都需要先启动一个运行环境, 然后调用 API 来 Deploy CloudFormation. 如何提供一套抽象能让不同的 CI 工具能达到相同的目的, 并且有相似的开发体验呢?
2. **即可将 DU 独立部署, 也可以将 DU 打包部署**: 对于 multi-repo 和 mono-repo 来说, CI 的编排方式很不一样. 例如 multi-repo 是每个 Deployment Unit 是一个 Project, 也是一个 Repo, 可以被单独部署. 而同时部署多个 Deployment Unit 往往需要自己写代码进行调度, 因为这涉及到 clone 多个 git 仓库, 并且不是每个 CI 系统都支持优雅地 invoke 其他 Repo 的 CI Workflow. 而 mono-repo 往往不同的 Deployment Unit 会放在不同的文件夹中. 然后用不同的 branch 来触发不同的 CI Workflow. 由于是一个 Repo, 把这些 Workflow 组合起来也比较容易, 无论 CI 工具支不支持对多个 CI Workflow 的编排, 组合, 复用, 我们都可以在代码层比较简单的写几个 wrapper 实现.

**一次开发, 到处运行**

解决这个问题的核心是抽象. 换言之, 你的 DevOps 脚本的核心功能的实现应该尽可能不依赖于任何 CI 平台特有的工具. 例如 Jenkins 使用 Groovy 进行编排, 而你的 DevOps Step 就不应该使用到 Groovy. 例如 GitHub Action 使用 YAML 执行 Terminal Command, 那么你的 DevOps Step 就不应该使用 YAML 来实现.

在 ``aws_ops_alpha`` 中, 所有的 DevOps Step, 例如 ``cdk deploy``, ``run unit test``, ``run integration test`` 都用 Python 封装成了 Terminal Command. 而按照顺序执行 DevOps Steps 的编排工作则交给 CI 系统去执行. 在这种设计下, 我们的 DevOps 逻辑都是用 Python 实现并封装成了 Terminal Command. 无论我们选择哪个 CI 系统, 我们都能轻易的按照顺序执行这些 Terminal Command 即可. 这就实现了 "一次开发, 到处运行".

**即可将 DU 独立部署, 也可以将 DU 打包部署**

解决这个问题的核心是分拆. 换言之, 我们先要确保能将 DU 独立部署. 然后用一个简单的自动化脚本将这些 DU 打包在一起部署. 我见过一些项目在一开始就设计为将很多个 DU 打包在一起部署, 在这种情况下你是无法在不大改代码的情况下将它们分拆的.


GitHub CI
------------------------------------------------------------------------------
在 GitHub Action 中, `Step <https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idsteps>`_ 是对 Terminal Command 的封装. 我们可以用 GitHub Action Step 来编排我们的 DevOps Step.

GitHub Action 有 `Reusing Workflow <https://docs.github.com/en/actions/using-workflows/reusing-workflows>`_ 功能. 你可以在一个 Workflow 中并行或者串行运行其他的 Workflow. 虽然它有最多 Nest 4 层的限制, 但是对于大部分应用场景来说已经足够了.


CodeBuild + CodePipeline
------------------------------------------------------------------------------
在 AWS CodeBuild 中, `Commands <https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-syntax>`_ 是对 Terminal Command 的封装, 我们可以用 Commands 来编排我们的 DevOps Step.

在 AWS CodePipeline 中, `Build Stage <https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html>`_ 可以用来并行或串行运行多个 AWS CodeBuild Job Run, 甚至是多个 AWS CodePipeline. 这样我们就可以将多个 DU 打包运行了.


CircleCI
------------------------------------------------------------------------------
在 CirCleCI 中, `Steps <https://circleci.com/docs/jobs-steps/#steps-overview>`_ 是对 Terminal Command 的封装. 我们可以用 CircleCI Step 来编排我们的 DevOps Step.

在 CircleCI 中, 你可以用 Workflow + Jobs 来部署多个 DU. 目前 (2024-01-01) 没发现 CircleCI 能在 Job 中运行其他的 YAML Workflow. 所以我们可能要将 DU 的 YAML 代码拷贝到新的 Workflow 中去.
