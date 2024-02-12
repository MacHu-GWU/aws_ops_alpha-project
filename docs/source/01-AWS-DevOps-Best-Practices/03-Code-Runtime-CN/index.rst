.. _code-runtime-cn:

Code Runtime (CN)
================================================================================


Overview
------------------------------------------------------------------------------
Code Runtime 指的是你的代码运行时所处的计算环境. 例如是在 laptop 上? 还是在 CI 的环境中? 还是在 AWS 计算环境中 (例如 Lambda)? 在 AWS 中常见的 Runtime 有:

- 可以被归为 local 本地开发环境的 runtime:
    - local laptop
    - AWS Cloud9
- 可以被归为 CI 环境的 runtime:
    - AWS CodeBuild
    - GitHub CI
    - GitLab CI
    - CircleCI
    - Jenkins
    - 还有一大堆 CI 产品
- 可以被归为 App 环境的 runtime, 取决于你用的什么 AWS Resource 来运行你的代码:
    - AWS Lambda
    - AWS EC2
    - AWS ECS
    - AWS Batch
    - 还有一大堆 AWS 的计算类服务

对于同一个业务逻辑的代码块, 在不同的 runtime 下的行为可能是不一样的. 例如你要读一个数据库密码, 在 laptop 上你可能直接去本地文件读了, 在 CI 的环境中你可能会去 AWS Parameter Store 中读, 在 AWS 的 Lambda 计算环境中你可能会去 Environment Variable 中读. 除非这段业务逻辑代码只会在一个 runtime 下运行, 否则你需要实现对应的 runtime 下这个代码的不同行为.


Detect Current Runtime
------------------------------------------------------------------------------
根据前面的介绍, 我们可能需要根据当前的 runtime 来运行不同行为所对应的代码块. 而如何检测当前的 runtime 呢? 这主要取决于你的项目会用到哪些 Runtime. 通常情况下一个 AWS 项目至少会用到 local, ci, app 三种 runtime. 下面是一些常见的检测当前 runtime 的方法:

- 对于不同的 CI 系统, 通常都会有一些内置的 Environment Variable. 例如 `GitHub Action <https://docs.github.com/en/actions/learn-github-actions/variables>`_ 中必有 ``GITHUB_ACTION``, `AWS CodeBuild <https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html>`_ 中必有 ``CODEBUILD_ID``. 我们可以用这些环境变量来判断.
- 对于一些 app runtime, 例如 `AWS Lambda Function <https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html>`_ 中必有 ``AWS_LAMBDA_FUNCTION_NAME``. 我们可以用这些环境变量来判断.
- 对于一些特殊的 runtime, 例如 EC2, 或者 Glue, 我们可以通过一些文件系统中的特殊目录或文件来判断.
- 对于一些没有通用的方法来判断的 runtime, 例如 ECS Task, local laptop, 我们可以在项目中约定一个特定的环境变量, 例如用 ``IS_ECS_TASK`` 环境变量来判断是否是 ECS Task. 我们可以在定义 ECS Task 的时候就把这个环境变量设置好. 开发者可以自行决定这个规则.


Runtime in Rule Set
------------------------------------------------------------------------------
Runtime 会参与到决定是否执行一个 DevOps Step 的决策逻辑中, 请阅读 :ref:`rule-set-cn` 获知详情.
