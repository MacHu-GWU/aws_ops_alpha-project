.. _rule-set-code-recipe-cn:

Rule Set Code Recipe (CN)
================================================================================
示例代码的背景信息请参考 :ref:`rule-set-cn`

之前我们介绍了我们可以通过维护一个 Truth Table 表格来判断在某种 Condition 的情况下, 是否要执行某个 DevOps Step.


Built in Rule Set
--------------------------------------------------------------------------------
下面我们列出了 ``aws_ops_alpha`` 项目中内置的一些服务于不同类型的项目的 Rule Set.

.. jinja:: doc_data

    {% for list_table in doc_data.truth_table_list_table_list %}
    .. dropdown:: {{ list_table.title }}

    {{ list_table.render(indent=1) }}
    {% endfor %}


Define Your Custom Rule Set
--------------------------------------------------------------------------------
当内置的 Rule Set 不能满足你的项目需求时, 你可以自定义你的 Rule Set. 本项目提供了一系列工具能让你轻松做到这一点.

我们以 ``aws_ops_alpha`` 中的 ``simple_lambda`` 为例, 展示一下我们是如何定义 ``simple_lambda`` 类型的项目的 Rule Set 的.

.. note::

    下面所有提到的模块都只是演示, 在你的项目中可以使用任何你想要的模块名.

1. 首先, 你先要想好你所有的 Condition 所有的可能取值. 例如 env_name, semantic_branch_name, runtime, step 可能的取值有哪些. 在 ``gen_code.py`` 这个模块中定义好. 下面给出了在 ``simple_lambda`` 中的例子.

.. dropdown:: aws_ops_alpha/project/simple_lambda/gen_code.py

    .. literalinclude:: ../../../../aws_ops_alpha/project/simple_lambda/gen_code.py
       :language: python
       :linenos:

2. 运行 ``gen_code.py``, 它会生成一个 ``should_we_do_it.tsv`` 文件的模版, 里面列出了所有的 Condition 的排列组合, 并且所有的 Conditional
 Step bool value 都是 False, 也就是不执行. 你可以将其拷贝到 Excel 或是 Google Sheet 软件中进行编辑. 定义在各种 Condition 下要不要执行某个 Step.

.. dropdown:: aws_ops_alpha/project/simple_lambda/should_we_do_it.tsv

    .. literalinclude:: ../../../../aws_ops_alpha/project/simple_lambda/simple_lambda_truth_table.tsv
       :language: csv
       :linenos:

3. 当编辑好之后, 将 Excel 中的数据拷贝回 ``should_we_do_it.tsv``, 然后执行 ``gen_code.py``. 它会根据 ``should_we_do_it.tsv`` 中的数据生成一个 ``simple_lambda_truth_table.tsv`` (就是 ``should_we_do_it.tsv`` 的拷贝), 和一个 ``simple_lambda_truth_table.py`` 模块. 这个模块提供了一个 ``truth_table`` 对象, 它的 ``truth_table.evaluate(case={"env_name": "sbx", "semantic_branch_name": "...", ...})`` 方法可以评估在指定的 Condition 情况下, 要不要执行这个 Step. 这个由脚本自动生成的 ``simple_lambda_truth_table.py`` 文件就是你用来做条件判断的主要模块.

.. dropdown:: aws_ops_alpha/project/simple_lambda/simple_lambda_truth_table.py

    .. literalinclude:: ../../../../aws_ops_alpha/project/simple_lambda/simple_lambda_truth_table.py
       :language: python
       :linenos:

4. 最后你还需要创建一个 ``rule_set.py`` 模块, 用来定义哪些 branch name 会被视为你所指定的 semantic branch. 下面给出了示例代码. 并且这段示例代码在 :ref:`semantic-git-branching-code-recipe-cn` 中也有提到过.

.. dropdown:: aws_ops_alpha/project/simple_lambda/rule_set.py

    .. literalinclude:: ../../../../aws_ops_alpha/project/simple_lambda/rule_set.py
       :language: csv
       :linenos:

至此, 你可以 import ``rule_set.py`` 和 ``simple_lambda_truth_table.py`` 模块来进行 DevOps Step 的条件判断了.


``aws_ops_alpha`` Built in Rule Set
------------------------------------------------------------------------------
.. jinja:: doc_data

    {% for project in doc_data.project_list %}
    .. dropdown:: {{ project.project_type }}/gen_code.py

        .. literalinclude:: ../../../../aws_ops_alpha/project/{{ project.project_type }}/gen_code.py
           :language: python
           :linenos:

    .. dropdown:: {{ project.project_type }}/{{ project.project_type }}_truth_table.py

        .. literalinclude:: ../../../../aws_ops_alpha/project/{{ project.project_type }}/{{ project.project_type }}_truth_table.py
           :language: python
           :linenos:

    .. dropdown:: {{ project.project_type }}/{{ project.project_type }}_truth_table.tsv

        .. literalinclude:: ../../../../aws_ops_alpha/project/{{ project.project_type }}/{{ project.project_type }}_truth_table.tsv
           :language: csv
           :linenos:

    .. dropdown:: {{ project.project_type }}/rule_set.py

        .. literalinclude:: ../../../../aws_ops_alpha/project/{{ project.project_type }}/rule_set.py
           :language: python
           :linenos:
    {% endfor %}
