.. _rule-set-cn:

Rule Set (CN)
================================================================================


Overview
------------------------------------------------------------------------------
在之前的文章中我们介绍了 :ref:`multi-environment-deployment-cn`, :ref:`code-runtime-cn`, :ref:`semantic-git-branching-cn` 的概念. 我们分别用 env_name, runtime, semantic_branch_name 来指代. 而在 AWS 项目的 DevOps 流程中, 会有很多 Step (步骤). 例如 run unit test, build artifacts, deploy CloudFormation stack 等. 而这些 Step 是否真的要执行则是由 env_name, runtime, semantic_branch_name 的组合来决定的. 所以这些 Step 也叫做 Conditional Step.

举个例子, 我们在一个 AWS Lambda 项目中, 在 ``semantic_branch_name = feature``, ``env_name = sbx``, ``runtime = ci`` 的时候我们希望运行 ``step = Unit Test``. 但是我们没有必要运行 ``step = Build Lambda Layer``, 因为 Lambda Layer 依赖层的构建比较费时间, 并且不是一个高频需求, 所以我们决定只在 ``semantic_branch_name = layer``, ``env_name = devops``, ``runtime = local or ci`` 的时候做.

在这个例子中, env_name, runtime, semantic_branch_name 各自都是一个条件, 我们称之为 ``Condition``. 在多个 ``Condition`` 排列组合的情况下, 是否要执行某个 Step 的 boolean value 的规则我们称之为 ``Rule Set``. 在我们这个例子中, 我们有三个 ``Condition``, 企业可以根据自己的情况决定是否要增加更多的 ``Condition``.


Truth Table
------------------------------------------------------------------------------
由上面的描述可知, 我们每一个 DevOps step 都依赖于三个维度来决定到底要不要做. 如果我们用 if else 这样的逻辑来实现 Conditional Step, 代码会变得非常难以维护. 举例来说, 如果 ``semantic_branch_name`` 有 5 种可能, ``env_name`` 维度有 3 种可能, ``runtime`` 有 3 种可能, DevOps 流程中有 10 个 ``step``, 那么我们需要写 5 * 3 * 3 * 10 = 450 个 ``if (semantic_branch_name == "..." and env_name == "..." and runtime == "...")`` 这样的代码. 而且这种代码可能会在代码库中的多个位置重复出现, 一旦有需求变更, 需要修改的地方也会非常多. 可想而知, 用 if else, 乃至是 match case 这样的语法来实现 Conditional Step 是非常不可取的.

这种问题的最佳解决方法是使用 Truth Table. Truth Table 是一个二维表格. 其中每一个 Condition 都有一列. 每一行都是所有的 Condition 的所有可能取值 + Step 的排列组合. 而最后一列则是一个 boolean value, 决定在 "这一行的条件下" 是否要执行这个 Step.

这种情况下我们只需要维护一个 Excel 表格或是 CSV 文件, 我们就可以去读取这个数据文件然后根据当前的 Condition 来做判断. 维护 Excel 表格可比维护 if else 要简单清晰多了. 并且由于这种 Rule Set 的定义是机器可读的, 我们甚至可以用数据来帮我们生成所有的 Condition 的 Enum 代码, 避免了手动同步 Rule Set 数据和代码.


Summary
------------------------------------------------------------------------------
在作者的职业生涯中, 做过了很多不同的 AWS 项目. 每一个项目的 DevOps 流程 (Step), Rule Set, CI 工具, 甚至编程语言都不一样. 而这套方法能够通过维护一个简单的 Truth Table 表格, 以及用一套通用的代码来来读取这个表格, 并且把 Conditional Step 的逻辑用 Shell Script 封装起来, 从而实现来在任何 CI 系统, 以及任何编程语言的项目, 甚至是非 AWS 的项目中都能够复用.

在过去, 每做一个新项目就要花很多时间开会导论这个 Conditional Step 的规则, 并且花很多时间写 if else 并且测试这些逻辑. 并且这些逻辑在过了一段时间之后, 就连我自己都不记得里面的规则了. 而这种方法可以让我们用一个简单的表格来可视化所有的规则, 并且无需维护大量代码就能在任何项目中使用, 大大提高了项目的 Go to market 效率, 并且使得更改项目流程变得非常容易, 而这往往是大部分项目做不到的, 因为他们修改了流程所涉及的代码改动太多.
