.. _monorepo-vs-multi-repo-cn:

Monorepo vs Multi-repo (CN)
==============================================================================


What is Monorepo and Multi-repo
------------------------------------------------------------------------------
在 AWS 项目中到底是使用 Monorepo 还是 Multi-repo 一直是有争论的. 我们这里先对 Monorepo 和 Multi-repo 做一个简单的定义.

首先我们定义 Deployment Unit (DU) 的概念. 一个 DU 是指需要独立部署的一组资源. 至于需不需要独立部署则由具体情况而定. 例如如果你有几个 Lambda Function 它们互相之间紧密结合, 那么就适合打包在一起部署. 通常一个 DU 对应着一个 AWS CloudFormation Stack.

Monorepo 是一种将多个 DU 的代码放在一个 Git repo 中的代码架构. 当然 Git 不是唯一的代码管理系统. 这些 DU 通常用 Folder 分隔开来. 这种设置的好处是所有人都能看到彼此负责的 DU 的代码. 并且那些每创建一个 DU 就要手动配置的事情也只需要配置一次. 因为这些配置基本上都可以用 Folder name 来参数化处理. 而使用 Monorepo 的设置对团队的素质要求较高, 需要每个人都能有基本的代码架构的认识. 而当代码库变得庞大以后, 每个开发者不需要 clone 全量代码, 而且多个 DU 之间还可能互相以弱耦合的形式交互. 这可能需要引入专用的代码管理系统来管理. 例如 Google 就有自己的代码管理系统.

Multi-repo 是一种将为每个 DU 创建各自独立的 Git repo 的代码架构. 这也是开源社区最常见的代码架构. 好处是天然的每个 DU 互相独立. 但坏处是哪些 DU 之间常见的设置和代码不容易被复用. 以及有一些为每个 Git repo 设置的工作是无法被自动化的, 这就意味着你 DU 多起来以后为每个 Git repo 进行配置的工作量还是挺大的. 当多个 DU 之间要联调的时候, 可能还要专门创建一个 Git repo 用来进行 Deployment 的编排.


Why I Recommend Monorepo
------------------------------------------------------------------------------
我在大部分的企业项目中推荐使用 monorepo 的架构. 理由如下:

1. 在实际的企业项目中, 大部分情况下一个项目组都会有很多 DU, 这些 DU 的部署相互独立, 但是彼此以弱耦合的形式联通. 这正是 Monorepo 擅长的场景. 当然, 我们不应该在一个 repo 中引入过多的 DU (20 个以内), 这样会导致代码库变得庞大. 在这种规模下, 我们一般不需要专用的代码工具, 使用标准的 Git 就可以了.
2. 在工程实践中, 如果我们一开始就将项目分拆成多个 DU, 那么将这些 DU 组合起来部署是比较容易的. 而如果一开始就把所有模块打包一起部署, 那么将它们分拆开是比较困难的.
3. 我比较推崇 Monorepo 还有一个很重要的原因. 你完全可以将 Monorepo 当成 Multi-repo 用, 也就是遵循 Monorepo 的代码架构, 但是下面只有一个 DU. 换言之, 如果公司制定了 Monorepo 的规范, 你是可以把它当成 Multi-repo 用的, 但反过来不行. 从投入产出的角度来看, 投入开发 Monorepo 的收益更高.


Tricks - Manage Monorepo in IDE
------------------------------------------------------------------------------
很多 IDE 都支持对代码库进行分析, 使得开发者能在各种函数定义和引用中互相跳转, 以及搜索整个代码库. 而使用 Monorepo 的话就会使得整个代码库变得庞大, 这样很多搜索操作就会很慢. 但这其实不是问题. 例如 PyCharm 支持将指定的 Folder 设为当前活跃项目, 将指定 Folder 设为 Ignore (`Controlling source, library and exclude directories <https://www.jetbrains.com/help/objc/controlling-source-library-and-exclude-directories.html>`_). VSCode 支持在 Settings 设定 ``search.exclude`` (`Settings precedence <https://code.visualstudio.com/docs/getstarted/settings#_settings-precedence>`_), 以及有一个插件 `Explorer Exclude <https://marketplace.visualstudio.com/items?itemName=PeterSchmalfeldt.explorer-exclude>`_ 可以使用户更容易做到这一点.


Tricks - Git Branch in Monorepo
------------------------------------------------------------------------------
很多团队都喜欢在 Git Branch 中使用 Ticket Number 或是 feature name 来描述这个 branch 是用来做什么的. 而如果使用了 monorepo, 就可能难以区分这个 branch 是属于哪个 DU 的. 但这其实不是问题, 你只要在你的所有命名规则之前要求加上项目名 (DU) 即可. 例如 ``project1/feature1``.


.. _tricks-deploy-multiple-project-together-in-monorepo:

Tricks - Deploy Multiple Project Together in Monorepo
------------------------------------------------------------------------------
在 Monorepo 的代码架构中, 通常每一个 DU 都会有一套自己的 CI, 甚至可能 CI 所用的系统都不一样. 那如果我们要将多个相关的 DU 打包在一起部署, 应该怎么做呢?

不同的 CI 系统通常会有自己的 API 用于 trigger build job. 而你只需要用一个类似 orchestrator 的东西, 可以是专用的工具例如 Airflow 或是 AWS Step Function, 也可以是一个专门的 bulk release CI job, 在里面并行或串行部署多个 DU 即可.
