CI Tools Integration
==============================================================================
本节我们主要介绍如何使用不同的 CI 工具来实现 aws_ops_alpha 的最佳实践.

这里有两个难点需要解决.

1. 市场上的 CI 工具很多, 它们的功能也不一样, 如何将不同的 CI 工具与 aws_ops_alpha 集成起来? 例如 GitHub Action 和 CircleCI 对 CI 代码的复用支持很好, 而 AWS CodeBuild 则没有这一功能. 例如 AWS CodePipeline 支持直接 Deploy CloudFormation 而无需启动一个运行环境, 而其他 CI 工具都需要先启动一个运行环境, 然后调用 API 来 Deploy CloudFormation. 如何提供一套抽象能让不同的 CI 工具能达到相同的目的, 并且有相似的开发体验呢?
2. 对于 multi-repo 和 mono-repo 来说, CI 的编排方式很不一样. 例如 multi-repo 是每个 Deployment Unit 是一个 Project, 也是一个 Repo, 可以被单独部署. 而同时部署多个 Deployment Unit 往往需要自己写代码进行调度, 因为这涉及到 clone 多个 git 仓库, 并且不是每个 CI 系统都支持优雅地 invoke 其他 Repo 的 CI Workflow. 而 mono-repo 往往不同的 Deployment Unit 会放在不同的文件夹中. 然后用不同的 branch 来触发不同的 CI Workflow. 由于是一个 Repo, 把这些 Workflow 组合起来也比较容易, 无论 CI 工具支不支持对多个 CI Workflow 的编排, 组合, 复用, 我们都可以在代码层比较简单的写几个 wrapper 实现.


Project and Deployment Unit
------------------------------------------------------------------------------



Mono Repo vs Multi Repo
------------------------------------------------------------------------------


pu
------------------------------------------------------------------------------


GitHub CI
------------------------------------------------------------------------------


CodeBuild
------------------------------------------------------------------------------
每个 Workflow 一个 CodeBuild

