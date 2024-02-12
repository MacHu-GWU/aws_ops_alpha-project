.. _multi-environment-deployment-cn:

Multi Environment Deployment (CN)
================================================================================


Overview
------------------------------------------------------------------------------
在传统软件工程实践中, 常常一个 App 会有多个 Environment, 从低到高分别是 ``sandbox`` (用于开发和实验的沙盒环境, 不会影响其他环境), ``test`` (测试环境), ``production`` (生产环境). 当然不同的项目可能还会有更多特殊作用的环境, 例如 ``qa`` (质量检测环境), ``staging`` (预发布环境) 等等, 我们这里就以 ``sandbox``, ``test``, ``production`` 为例进行讨论. 这样做的目的是对不同的环境的数据和操作权限进行隔离. 例如单元测试在 ``sandbox`` 中进行, 使用 Dummy data 即可. 而 ``test`` 测试环境可能只有生产环境中 10% 的数据. 而普通开发者可能只能允许有 ``sandbox``, ``test``, 以防不小心对生产环境造成损失.

在 AWS 云时代, 这种实践常常用 AWS Account 来实现. AWS Account 之间的数据, 网络, 权限天然是隔离的. 所以给每一个 Environment 一个单独的 AWS Account 是一个很好的选择. 在企业级的项目中, 通常会使用一个中心化的 DevOps 环境, 以及多个 Workload 环境来部署 App. DevOps 环境一般不部署真正的 App, 而是专注管理运维所用的资源, 例如 CI Job runner, 以及部署所用到的 Deployment Artifacts. 而 Workload 环境则是真正用来部署 App 的. 这也是 AWS 官方推荐的最佳实践.

.. note::

    在后续的文档中, 我们会用 **1 + N** 这个术语来指代一个 DevOps 环境以及多个 Workload 环境的组合.

本文我们来详细讨论跟 Multi Environment 相关的一些话题.


Cross Environment Access Control
------------------------------------------------------------------------------
如前面所说, DevOps 环境是用来跑 CI/CD 的自动化代码的, 以及上传部署所用到的 Artifacts. 而部署的任务则是把 App 部署到 Workload 环境中. 这就意味着 DevOps 环境要有对 Workload 环境中的资源进行部署的能力. 这一点通常用 assume role 技术解决, 让 DevOps 上的 Role assume Workload 上有部署权限的 Role. 这个 Role 我们叫做 Deployer Role. 以后提到 Deployer Role 就暗指这个 Role 是指位于 Workload Account 中的. Deployer Role 也要有能从 DevOps Account 中获取部署所需的 Artifacts 的权限. 这个权限通常是通过 Resource Policy 实现的. 在 DevOps 环境中创建用于 Host Deployment Artifacts 的资源的时候, 用 Resource Policy 显式地给 Workload AWS Account 或是 Deployer Role 读权限. 一些常见的例子有 S3 Bucket Resource Policy (参考 `Bucket owner granting cross-account bucket permissions <https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-walkthroughs-managing-access-example2.html>`_), ECR Repository Policy (参考 `Private repository policies <https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-policies.html>`_, `How can I allow a secondary account to push or pull images in my Amazon ECR image repository? <https://repost.aws/knowledge-center/secondary-account-access-ecr>`_, AWS Secret Manager Policy (参考 `Permissions to AWS Secrets Manager secrets for users in a different account <https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_examples_cross.html>`_) 等等.


How many Workload Environments do I need
------------------------------------------------------------------------------
对于不同的项目, 一共需要多少个环境是要视具体情况而定的. 但是通常情况下, **一般都至少要三个 Workload 环境**, **sbx** 是完全隔离的, 用于开发. **tst** 是用于 integration test 和 end to end test 的. 而 **prd** 则是真正的生产环境. 对于有些项目还可能会有 stg 用于克隆生产环境中的数据, 用真实数据进行测试, 也可能有 qa 用户质量检查. 例如, 对于企业中的关键业务系统 4, 5 个环境都不算多. 而对于快速迭代的创业公司可能 2 到 3 个环境就够了. 而对于个人项目, 1 个环境也不是不可以.


How many AWS Accounts do I need
------------------------------------------------------------------------------
在 AWS 官方文档中, 推荐给每一个环境一个单独的 AWS Account, 这样有助于权限隔离. 但是对于有的团队和项目的特殊需求, 它们希望将这些环境全部都放在一个 Account, 或是将几个环境 (例如把 non-prod 的几个环境放在一个 Account, 而 production 单独一个) 打包放在一个 Account 中. 这种情况下的隔离通常是通过 resource naming convention 以及 IAM role 权限实现的. 具体做法则是给每个环境中的 App 单独一个 IAM Role, 其 IAM policy 中的 ``Resources`` 一项用 ``regex`` 显式指定只允许访问该环境中的 Resource.

总结下来, 一般我们会有这么几种配置方法:

1. devops 和 workload 每个环境都是一个单独的 AWS Account (推荐).
2. devops 单独是一个 account, 所有 Non-prod 都是一个 account, prod 单独是一个 account (也很常见).
3. devops 单独是一个 account, 所有的 workload account 是一个 account (早期实验性质的项目常用这种方式).
4. devops 和所有 workload 都是一个 account (早期实验性质的项目常用这种方式).


Persona Access Control
------------------------------------------------------------------------------
在一个 Multi Environment 项目中工作的团队成员通常有以下几种 Persona (角色) (注, 下面列出了所有可能的角色, 具体项目中可能并不需要所有的角色):

1. Admin: 项目的管理员, 有着最高权限, 可以操作所有环境. 通常是由既懂业务又懂技术, 并且有 DevOps 背景的人担任. 一般是 DevOps 的头.
2. QA: 对系统进行质检测试. 通常是由非常了解业务的人担任. 有一定的技术背景最好, 但不是必须得.
3. DevOps: 负责项目的运维, 有着比较高的权限, 通常有操作除 Production 之外的所有环境的权限, 并有 Production 的只读权限. 通常要对项目的交付负责.
4. Developer: 开发人员, 有着比较低的权限, 通常只有对 sbx 和 tst 环境的权限.

以上的设定, 我们需要为这些角色配置好权限, 使得他们能胜任自己的工作, 但又不会越权. 这些权限对应的一般是一个 IAM Role (有些公司倾向于用 IAM User, 但不推荐).

1. Admin: 有所有环境的 AWS Account 的 Admin 权限.
2. QA: 通常有 QA 环境的可读, 可 Invoke 的权限, 但是不能更改任何资源.
3. DevOps: 通常有所有环境的可读, 可写, 可 Invoke 的权限, 但是不能更改 Production 环境的资源.
4. Developer: 通常有 sbx 和 tst 环境的可读, 可写, 可 Invoke 的权限. 并且有其他环境的只读权限. 对于有敏感数据的业务, 则不能给 production 的只读权限.


Detect Current Environment Name
------------------------------------------------------------------------------
在你的代码中肯定是要用某种方式获得当前的 ``env_name``. 这个值非常重要. 例如你可能需要用这个值来决定去哪个 AWS Parameter Store 获取 Config, 从哪个 S3 Bucket 中读数据 (例如 ``my-${env_name}-bucket``). 所以我们就需要一种方法来获取这个值.

我们推荐使用将当前所在的 ``env_name`` 的值保存在 ``ENV_NAME`` 这个环境变量中. 例如你在部署你的 AWS Lambda 的时候, 就把这个值写入到 ``ENV_NAME`` 环境变量. 例如你在 CI 的环境中, 想将 App Deployment 到某个环境中, 那么执行这个步骤的脚本之前, 先将 ``ENV_NAME`` 设置为正确的值. 我们还推荐使用 ``USER_ENV_NAME`` 来强制指定 ``env_name`` 的值, 以 override ``ENV_NAME`` 中的值. 这样可以在有特殊需求的时候强制切换环境. 平时 ``USER_ENV_NAME`` 是没有值的.


Environment Name in Rule Set
------------------------------------------------------------------------------
Environment Name 会参与到决定是否执行一个 DevOps Step 的决策逻辑中, 请阅读 :ref:`rule-set-cn` 获知详情.
