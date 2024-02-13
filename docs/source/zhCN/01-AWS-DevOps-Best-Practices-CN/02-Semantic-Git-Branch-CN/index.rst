.. _semantic-git-branching-cn:

Semantic Git Branching (CN)
================================================================================


What is and Why Semantic Git Branching
------------------------------------------------------------------------------
Semantic Git Branch 是一种在赋予 Git branch name 一定的语义的最佳实践. 这些语义可以用来在 DevOps 或业务逻辑中进行条件判断. 在某些 branch 下是一种流程, 在另一个 branch 下是另一个流程.

举例来说, 我们希望在任何名字类似于 ``feat``, ``feature/description``, ``feature-123/description`` 的 Git branch 都被视为 :bdg-success:`feature` branch. 而在 feature branch 上我们的 CI 只负责对代码进行 unit test. 什么 artifacts 的构建, deployment 之类的一概不做.  而名字为 ``app/description`` 的 Git branch 被视为 :bdg-warning:`app` branch, 在 app branch 上我们除了进行 unit test, 还会部署 App, 以及进行 integration test.

在上面的例子中, :bdg-success:`feature` 和 :bdg-warning:`app` 就是 semantic name, 也就是语义.

这种项代码管理规范能降低团队成员的沟通成本, 看到 branch 名字不用沟通就知道大概做了什么. 同时也能减少犯错, 例如能避免 feature branch 上不小心将还未完善的代码 deploy 到了 production. 因为我们可以制定一些规则, 定义在各种 semantic name 下能做什么, 不能做什么. 然后用自动化脚本来实现这一规则.


Semantic Branch Naming Convention
------------------------------------------------------------------------------
对于 multi-repo (每个项目都是一个单独的 Git repo), 我们推荐使用 ``${semantic_name}/${description}`` 的格式. 对于 mono-repo (一个 Git repo 中包含了多个项目, 并用文件夹隔离开), 我们推荐使用 ``${project_name/${semantic_name}/${description}`` 的格式.

而这个 ``semantic_name`` 和对应的语义可以是多对一的关系. 例如 ``feature``, ``feat`` 都对应着 Feature branch 这一语义.


Semantic Branch in Rule Set
------------------------------------------------------------------------------
Semantic Branch 会参与到决定是否执行一个 DevOps Step 的决策逻辑中, 请阅读 :ref:`rule-set-cn` 获知详情.
