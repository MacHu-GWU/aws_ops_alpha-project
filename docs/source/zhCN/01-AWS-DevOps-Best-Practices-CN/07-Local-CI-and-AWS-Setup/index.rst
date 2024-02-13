.. _local-ci-and-aws-setup-cn:

Local, CI and AWS Setup (CN)
==============================================================================


Overview
------------------------------------------------------------------------------
本文档假设我们拿到了一个全新的大型 AWS 项目, 这个大型项目会备份拆成许多需要被独立部署的子系统. 这些子系统所用到的技术栈各不相同. 例如有的是 Lambda 项目, 有的是 Glue ETL 项目, 有的是 StepFunction 编排项目, 有的是 AWS Batch 容器项目. 我们扮演架构师和 Tech Lead 的角色, 来设计这个项目的架构, CI/CD 流程, 以及开发环境的搭建.


1. Multi-Environment Setup
------------------------------------------------------------------------------


How many environments do we need
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**首先我们要决定我们的项目要用几个 Environment**. 最少我们需要一个 devops 环境用来管理 artifacts, 以及至少两个 workload 环境, 包括 sbx 用来开发, 和 prd 用来做生产环境. 在此之外, 我们还可以添加例如用于端到端测试的 tst 环境, 和用来做生产流量测试的 stg 环境.

.. note::

    为了方便说明, 我们后续假设使用了 devops, sbx, tst, prd 四个环境.


What resources do we need in each environment?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**其次我们要决定每个环境都需要什么资源**. 例如 configuration 数据是集中放在 devops 环境? 还是把属于不同 workload 环境中的 configuration 放在各自的环境中? 例如容器镜像是集中放在 devops 环境? 还是每个 workload 环境都拷贝一份?

.. note::

    这些决策没有说哪个就一定最优, 需要视情况而定. 但是在条件允许的情况下, 凡是不可变的大型 artifacts, 例如容器, 和二进制大文件, 尽量只在 devops 环境中维护一份, 并 share 给 workload 环境. 凡是涉及到各个环境自己的数据, 包括配置数据, 出于隔离和安全的考虑, 尽量让每个 workload 环境维护自己的数据, 并在 devops 环境中集中备份.


2. AWS Setup
------------------------------------------------------------------------------
然后我们要确定需要使用几个 AWS Account, 每个 AWS Account 分别用来做什么. 之后的 CI Setup 和 Local Setup 都需要根绝这个决定来做相应的调整.

AWS 官方称 "An AWS account is a unit of security protection". 而使用多个环境不仅仅是为了能在非生产环境中进行充分测试, 还有数据和权限隔离的需求. 例如你不希望非生产环境中的计算资源能访问生产环境中的数据, 又例如你希望初级开发者只接触非生产环境, 而只有管理员能接触生产环境. 这就使得 AWS Account 天然适合作为不同环境隔离的边界.

当然, 用来做隔离的方式有很多, 有 IAM Permission, 也有 Resource Policy. 例如我们可以将多个环境放在一个 AWS Account 中, 通过 naming convention 和 IAM role 来进行隔离. 无论选择哪种方案, 我们都希望以数据安全和隔离为第一优先级, 以工作量为第二优先级来做决策.

**下面我们来看看用多个 Account 和用一个 Account 的优缺点**.

1. 多个 Account
    - 优点:
        - 天然隔离, 比较安全. 如果你不做特别的事情, 安全天然有保障. 除非你做了特定的设置, 而这些设置是天然可以被 audit 的, 如果有人做了什么危险的事情, 后续很容易查出来.
    - 缺点:
        - 为了实现跨 AWS Account 的访问, 需要额外的设置, 会带来额外的工作量.
        - 并且从开发者的角度, 在多个 AWS Account 之间切换会需要在浏览器中切换登录, 并导致已经打开的窗口失效, 被迫重复刷新, 比较的麻烦.
        - 跨 AWS Account 管理资源需要额外的设置, 比较不容易弄清楚每个 Account 中有什么.
2. 单个 Account
    - 优点:
        - 设置简单, 所有的隔离都可以用脚本程序 + IAM 来实现. 在开发的过程中无需切换 AWS Account.
    - 缺点:
        - 不够安全, 在一个 Account 内限制不同的人和不同的 App 只能访问它所负责的环境上的资源需要额外的设置, 并且容易错漏.

**综上, 我们做决策的思路可以简化成以下几点**

1. 如果安全非常重要, 换言之出安全问题的代价很大, 果断多个 Account.
2. 如果有人员隔离需求, 不同的人只能访问自己负责的环境, 果断多个 Account.
3. 如果是一些不涉及敏感数据, 安全也不重要的小项目, 例如专注于自动化的项目, 可以考虑单个 Account.

**如果使用多个 Account, 需要做的事情**

1. 配置 devops account 的登录权限. 通常是所有的开发者都可以用 SSO + IAM Role 或者 IAM User + User Group 登录 devops Account. 根据人员的职能, 给开发者, 测试, 管理员等不同的权限. 如果用 SSO 登录, 那么不同的登录用的 IAM Role 就对应不同的职能, 而如果用 IAM User 登录, 则 User Group 就对应不同的职能.
2. 你需要配置 cross account IAM permission. 通常是一个 devops Account 上的 IAM Role 要能 assume workload account 上的 IAM Role 来到 workload account 上做事情. 以及 devops Account 上的一些资源需要允许 workload 上的 IAM Role 来读数据, 例如拉取 artifacts 或是容器镜像. 我推荐使用 `cross_aws_account_iam_role <https://github.com/MacHu-GWU/cross_aws_account_iam_role-project>`_ 工具配置. 如果你有一些非 AWS 的计算资源, 例如 GitHub Action CI, 你可能还需要用外部的 Identity Provider, 例如 OpenId, 来给这些外部计算资源 AWS 权限.
3. 每个 Account 上需要预先配好一些通用的资源, 例如用于存放文件的 S3 Bucket, 例如给管理员用的每个 Account 一个的 IAM Principal (User or Role). 因为只有管理员有了对应权限, 才能方便的自动化配置 #1, #2 以及其他的一些事情.

**如果使用单个 Account, 需要做的事情**

1. 类似的, 需要配置登录权限, 这点跟 #1 一样.
2. 为每个 environment 中的资源定义 naming convention, 例如给每个 environment 一个 prefix. 然后根据 naming convention 为每个 environment 创建 IAM Role, 使得它能操作属于特定 environment 的 IAM Role.
3. 类似的, 为单个 Account 配置好一些通用资源, 例如存放文件的 S3 Bucket. 例如管理员用的 Admin IAM Principal.


3. Local Setup
------------------------------------------------------------------------------
下一步我们就要配置好本地开发环境了. 这个过程对于管理员和普通开发者来说基本一致, 只是管理员的权限会比较高.

**简单来说, 本地配置的目标就是要允许开发者能访问各个 AWS Account 以及各个 Environment**.

这里的原则是, 给每个 Environment 所对应的 AWS Account 在本地配置一个 AWS CLI Profile. 无论你使用多个还是单个 Account, 无论这些 Environment 所使用的 Credential 是不是同一个, 你都是有几个 Environment 就创建几个 Profile. 因为使用单个 Account 以及使用单个 Credential 只不过是使用多个 Profile 的特例. 这样无论你使用的是单个还是多个, 你才能用一套自动化代码来搞定.

我认为的最优方法是:

1. 管理员在每个 AWS Account 中创建一个 IAM User 给自己用 (在 AWS Setup 中就应该做完了). 并且在本地配置好 AWS Profile.
2. 开发者用 SSO 登录, 管理员为开发者配置好 IAM Role (在 AWS Setup 中就应该做完了), 开发者在本地配置好 SSO 的 Profile 以及对应的 workload account 的 profile


Laptop Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
无论你是管理员还是开发者, 你都需要在本地配置 1 + N 个 AWS CLI Profile. 其中 1 是 devops 环境的 IAM Principal, 而 N 是 workload 环境的 IAM Role. devops 的 IAM Principal 需要能 assume workload 环境中的 IAM Role. 就算你是开发者, 没有访问 production 环境的权限, 但是这个 IAM Principal 也要有, 只不过里面的权限是全部 deny. 这样做才能用一套自动化代码来搞定所有情况.


AWS Cloud 9 Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Cross Account IAM Access**

本小节我们详细讨论如何在 Cloud 9 中对多个 Workload AWS Account 进行访问.

Cloud 9 的本质是一个 AWS EC2, 我们通常不会在 Cloud 9 上手动编辑 ``~/.aws/credentials`` 文件. 根据最佳实践, 我们需要给这个 Cloud 9 一个 IAM Instance Profile, 其本质是一个 IAM Role, 然后给这个 Role 能 Assume 其他 AWS Account 上的 Role 的权限.

我推荐你手动配置好 Cloud 9 的 IAM Role 之后, 使用 `cross_aws_account_iam_role <https://github.com/MacHu-GWU/cross_aws_account_iam_role-project/tree/main>`_ 这一 Python 工具自动化地配置好 Workload AWS Account 上的 IAM Role 以及 Cross Account Access 的权限.

**How does Cloud9 Knows Which IAM Role to Assume**

我们需要约定一个规范, 让 Cloud 9 自己就知道如何去找到它应该 Assume 的 IAM Role. 有多种方法可以实现这一点, 例如将 Environment Name 到 IAM Role 的映射保存在环境变量中, 或是保存在一个约定的文件中, 或者直接写死在源代码中. 我推荐通过修改 Cloud9 上的  ``~/.bashrc`` 或 ``~/.bash_profile`` 文件, 添加 ``DEVOPS_IAM_ROLE_ARN``, ``SBX_IAM_ROLE_ARN``, ``PRD_IAM_ROLE_ARN`` (如果你有更多的环境则你可以添加更多) 环境变量. 这篇 AWS 官方文档详细介绍了这一方法:

- `Working with Custom Environment Variables in the AWS Cloud9 Integrated Development Environment (IDE) <https://docs.aws.amazon.com/cloud9/latest/user-guide/env-vars.html>`_

aws_ops_alpha 项目中有一个 :meth:`aws_ops_alpha.boto_ses.impl.AlphaBotoSesFactory.get_env_role_arn` 抽象方法, 可以让用户自定义在不同的 runtime 中, 给定一个想要访问的 environment name, 如何找到应该 assume 的 IAM role 的 ARN. 你可以继承这个类, 并参考下面的例子实现这个方法.

.. code-block:: python

    import dataclasses

    @dataclasses.dataclass
    class MyBotoSesFactory(AlphaBotoSesFactory):
        if self.runtime.is_aws_cloud9:
            return os.environ[f"{env_name.upper()}_IAM_ROLE_ARN"]
        elif ...
        else:
            ...


4. CI/CD Setup
------------------------------------------------------------------------------
**这一步的目的是让我们使用的 CI/CD 工具能够对 AWS Account 进行访问. 以及能跟 Git 仓库的各种事件进行集成**.

**选择 Git 仓库和 CI/CD 工具**

首先我们要考虑的是选择 git 仓库托管和 CI/CD 工具. 通常这两个是紧密结合的. 例如如果你 git 仓库是在 GitHub 上, 那 CI/CD 工具一般也用 GitHub Action. 反过来如果你的 CI 工具是 AWS CodeBuild, 那么你的 git 仓库一般会用 AWS CodeCommit.

由于 git 仓库产品的功能差异比较小, 而 CI/CD 工具的功能差异比较大, 所以一般优先考虑 CI/CD 工具.

**有哪些 CI/CD 工具可供选择**

市场上常用的 CI/CD 工具很多, 对于 AWS 项目来说可以大致分为 AWS 原生和非原生两类. 因为从配置的方面来说, 给 AWS 原生工具配置 AWS 权限很简单, 而给非原生工具配置 AWS 权限会有一些额外步骤. 下面列出了可供选择的工具:

1. AWS 原生的 CodeBuild + CodePipeline.
2. 非 AWS 工具, 例如 GitHub Action, GitLab CI, BitBucket Pipeline, CircleCI,  Jenkins 等等. 我个人最推荐的是 GitHub Action, 因为它的设计最为现代化, 并且有最为活跃的第三方库的社区, 这种社区活跃度会导致这个工具越来越强, 越来越流行.

**我要如何做决策**

1. 首先考虑你有没有自由度, 有没有例如公司强制规定要求你必须使用某一个产品, 如果有, 那你没得选择, 照做即可.
2. 其次你要考虑你的数据安全需求, 你的数据 (包括代码, Artifacts) 是否允许离开 AWS 环境, 如果不可以, 那你只能使用 AWS 原生工具.
3. 第三要考虑团队的知识储备, 如果你的团队对于切换工具的意愿很低或是没有能力和时间学习适应新工具, 那么你只能使用团队已经熟悉的工具. 如果你的团队人员流动大, 你就要考虑补充新人员的时候, 什么 CI 工具比较好招人.
4. 最后才是考虑 CI 工具的功能是否能满足你的需要.

**CI/CD 工具的需求**

衡量一个 CI/CD 工具我们一般要考虑如下需求

1. 是否能和不同的 SVC (source code version control) 集成的能力.
2. 能否灵活的用 push, branch, pr 等 event 自定义触发规则.
3. 是否有灵活的编排功能, 让各个步骤之间可以有依赖关系, 串行执行, 并行执行, 允许部分失败等.
4. 是否有直观的 UI, 能让管理者迅速了解系统状态, 能让开发者迅速的定位问题.
5. 是否支持 CI 代码的复用 (例如 GitHub Actions, CircleCI Orb).
6. 是否支持人工 approve.
7. CI 系统是否支持 API 远程调用.


AWS CodeBuild + AWS CodeCommit Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CodeBuild 的权限来自于它的 IAM Role. 所以我们只需要在 Devops 上创建好 CodeBuild Project 以及它的 IAM Role, 然后在 workload account 上创建好对应的 IAM Role 并允许 CodeBuild IAM Role assume 它们.

这里有个特例, 有的用户会将 Jenkins 集群部署在 AWS 上, 这时 Jenkins 集群本身就是 EC2, 底层也是使用的 IAM Role, 这就跟 CodeBuild 一样了.


Non AWS CI/CD Tools Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
这一类的 CI 系统的 AWS 权限管理策略都是类似的. 基本上都是在 CI 系统中配置好 DevOps Account 的 IAM Principal 权限, 然后再 workload account 上创建好对应的 IAM Role 并允许 DevOps Account 的 IAM Principal 能够 assume 它们.

而配置 DevOps Account 的 IAM Principal 的方式大体分为两种:

1. 如果 CI 供应商跟 AWS 有合作, 例如 GitHub 和 AWS 支持 OpenID 登录, 无需显式提供 credential, 那么优先使用这一方式.
2. 在 DevOps AWS Account 创建 IAM Role, 然后把 credential 上传到 CI 的供应商的密码管理系统中. CircleCI 就是使用的这一方式.
