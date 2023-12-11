Multi Environment Deployment (CN)
==============================================================================



What is Multi Environment
------------------------------------------------------------------------------
在经典生产级项目中, 通常会使用一个中心化的 DevOps 环境, 以及多个 Workload 环境来部署 App. DevOps 环境一般不部署真正的 App, 而是专注管理运维所用的资源, 例如 CI Job runtime, 以及部署所用到的 Artifacts. 而 Workload 环境则是真正用来部署 App 的. 而将这些环境放在不同的 AWS Account 上的好处是便于给团队中的不同人员不同的权限, 便于管理. 例如管理员可以管理 DevOps 上的全部资源. 每个 App 的负责人可以编辑 Production, 而普通开发者只能编辑 Sandbox, 而不能编辑 Production.


What is DevOps Environment
------------------------------------------------------------------------------
如前面所说, DevOps 环境是用来跑 CI/CD 的自动化代码的, 以及上传部署所用到的 Artifacts. 而部署的任务则是把 App 部署到 Workload 环境中. 这就设计到跨环境权限管理问题:

1. DevOps 环境要有对 Workload 环境操作的能力. 这一点通常用 assume role 技术解决 (让 DevOps 上的 Role assume Workload 上的 Role).
2. Workload 环境要有能从 DevOps 环境中 pull artifacts 的能力. 这一点通常用 Resource Policy 技术解决. 例如 AWS S3 bucket policy.


How many Workload Environment I need
------------------------------------------------------------------------------
对于不同的项目, 一共需要多少个环境是要视具体情况而定的. 但是通常情况下, 一般都至少要三个 Workload 环境, sbx 是完全隔离的, 用于开发. tst 是用于 integration test 和 end to end test 的. 而 prd 则是真正的生产环境. 对于有些项目还可能会有 stg 用于克隆生产环境中的数据, 用真实数据进行测试, 也可能有 qa 用户质量检查.

本项目不对 Workload 环境的数量做限制, 而是交给用户自己决定. 无论用户有多少 Workload 环境, 本项目提供了一些工具使得这些 Workload 环境中的特殊规则可以轻易的和 App 代码集成.


How many AWS Account I need
------------------------------------------------------------------------------
在 AWS 官方文档中, 推荐给每一个环境一个单独的 AWS Account, 这样有助于权限隔离. 但是对于有的团队和项目, 是有将这些环境全部都放在一个 Account, 或是将几个环境 (例如把 non-prod 的几个环境放在一个 Account, 而 production 单独一个) 放在一个 Account 中的需求的. 这种情况下的隔离通常是通过 resource naming convention 以及 IAM role 权限实现的.

本项目不对这一点做任何限制, 用户可以使用任何策略. 本项目提供了一个抽象层, 用户只要自己实现即可.