
CICD Step
==============================================================================
``aws_helpers`` 目录下都是一些实现了 CI/CD Step 的逻辑的辅助函数. 这些函数专注于功能, 不会打印 log, 也不会判断是否要运行这些 Step. 在最终的带 log, 带判断的 CI/CD Step 函数中我们会调用这些辅助函数.

``project`` 目录下都是 带 log, 带判断的 CI/CD Step 逻辑. 这些函数的逻辑中不会使用任何除了入参以外的任何参数. 因为这里的函数在实际的项目中要再被封装一层,  把实际项目中的数据传递到这些函数的参数中.



CI/CD Orchestration
------------------------------------------------------------------------------
本节我们介绍在本项目中我们如何实现用一套 Orchestration 框架兼容不同的 CI/CD product.

由于不同的 CI product 中有很多不同的术语. 为了后续的描述方便, 我们将 Orchestration 其抽象成一个有向无环图 Dag, 每个节点是一个 **Step**. 这些 Step 是要在 Runner 中运行的, 这个 Runner 可以是虚拟机也可以是容器. 不同的 Runner 值得是为执行一系列 Step 所临时创建的计算资源. Runner 的概念在 GitHub Action 中叫做 Job Run, 在 AWS CodeBuild 中叫 CodeBuild project job run. 这些 Step 可以在不同的 Runner 中运行, 也可以在同一个 Runner 中运行. 举例来说, 如果我们用 GitHub Action, 这些 Step 可以在一个 Job 中运行, 也可以在不同的 Job 中运行. 而如果我们用 AWS CodeBuild, 则这些 Step 可以再一个 CodeBuild project job run 中运行, 也可以在不同的 Job 中运行.

为了描述方便, 我们会使用术语 **Step** 来指代为了达到某一个目的所需的一连串命令, 而 **Job** 指的是在一个 Runner 的生命周期内运行多个 Step.


One Job or Multiple Job
------------------------------------------------------------------------------
我们完全可以将所有的 Step 用 if / else 逻辑组织起来, 在一个 Job 中运行. 但是出于许多原因, 我们将 Step 分散到多个 Job 中运行. 这些原因有:

1. 我们希望用多个 Job 来并行执行一些 Step 以提高速度.
2. 每个 Step 做的事情涉及到不同的权限, 我们需要让具有特定权限的 Job Runner 来执行特定的 Step 以实现权限隔离.
3. 有些特定的 Step 需要特别大的内存和磁盘, 所以我们使用专用的 Job Runner 来执行特定的 Step.

本项目不对 Step, Job 的搭配做任何假设, 用户可以自由选择. 但是本项目提供了最佳实践的具体实现. 在本项目中, 我们会有 1 + N 个 Job. 1 个 Job 专门用来运行单元测试和 build artifacts. 而另外 N 个 Job 用来部署 App 到不同的环境以及运行 Integration Test.




