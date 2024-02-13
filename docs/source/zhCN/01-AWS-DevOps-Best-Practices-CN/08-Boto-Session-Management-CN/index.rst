.. _boto-session-management-cn:

Boto Session Management (CN)
==============================================================================


Overview
------------------------------------------------------------------------------
在 AWS 项目中, `boto session <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/session.html>`_ 是跟 AWS API 交互的核心对象. 在 :ref:`cross-environment-access-control` 中我们提到了, 在 DevOps
 中运行自动化脚本时, 需要将 Deployment Artifact upload 到 DevOps 环境中, 也需要将 App 部署到 Workload 环境中. 这就涉及到 Cross Account IAM Role 的使用. 在你的 DevOps 代码中, 你可能需要用 DevOps 的 IAM Role assume 一个 Workload 的 IAM Role. 在实际项目中, 我们应当尽量避免在所有需要使用 boto session 时候临时编写一段创建该 boto session 的代码块. **正确的做法是应该将 devops boto session, workload boto session (包括 sbx, tst, prd 的 session 的枚举) 都封装为函数, 以便在代码库的其他部分中引用**. 有些 CI 系统的插件可以自动化一些例如 assume role 的工作, 只要你遵守该插件约定的规范. 但是这些插件系统的可定制性是远远不如一段 Python 函数的. 有一些情况下插件约定的规范对我们的项目并不适用. 而你用 Python 函数的话完全可以利用这些插件, 并在基础上进行定制, 大大增加了灵活性. 并且这些函数还能在你的代码库中进行复用. 而这些 CI 插件只能在 CI 脚本中使用, 无法在 App 代码中使用.
