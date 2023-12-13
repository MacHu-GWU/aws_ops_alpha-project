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