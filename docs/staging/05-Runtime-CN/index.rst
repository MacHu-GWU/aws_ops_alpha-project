Runtime
==============================================================================
Runtime (简称 RT) 的概念指的是一个用来运行代码的计算资源的类型. 在一个项目周期中, 代码会在本地开发者电脑上运行, 会在 CI/CD 的机器上运行, 也会在最终的 App 的运行环境上运行, 其中 App runtime 可能是 EC2, 可能是 Container.

我们可以将 RT 大致分为三类. 每一类下又分几个子类:

1. 本地开发 RT: 开发者主力写代码的 RT.
    - local: 开发者本地的电脑.
    - aws_cloud9: 我们常有用服务器进行开发的需求, 因为服务器的网络环境和权限可能跟生产环境更近. 例如 AWS Cloud9 是一个 AWS 托管的开发机器. 我们只是用它来举例, 我们用 aws_cloud9 指代一切服务器开发环境.
2. CI/CD RT: 各种 CI/CD 的 RT
    - GitHub Action
    - CodeBuild
3. App RT: App 代码最终运行的 RT. 主要分为虚拟机和容器两类. AWS 中常见的 App RT 如下.
    - EC2:
    - Lambda:
    - Glue:
    - Batch:
    - ECS:


Local Laptop Setup
------------------------------------------------------------------------------



AWS Cloud 9 Setup
------------------------------------------------------------------------------
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
