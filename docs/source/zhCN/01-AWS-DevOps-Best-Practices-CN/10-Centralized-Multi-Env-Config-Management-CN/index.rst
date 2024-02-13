.. _centralized-multi-environment-config-management-cn:

Centralized Multi Environment Config Management (CN)
==============================================================================


Common Mistake in Config Management
------------------------------------------------------------------------------
在前面的文章中我们提到了一个 AWS 项目可能会有多个环境. 每个环境的 Config 可能是不一样的. 所以在项目中专门用一个模块来管理 Config 数据是非常有必要的. 但是在生产实践中, 很多项目的 Config Management 的模块都会犯一些常见的错误. 比如:

- 在代码中用 hard code, 或是引用了一个非 Config 模块的变量来指定某个值. 而这个值在项目的生命周期内可能会发生变化. 并且这个值在代码库中用到了不止一次.

    当值发生变化时, 你需要找到这个值在哪里被定义的然后修改它. 由于这个值不是在 Config 模块中被定义的, 你需要了解整个代码库才知道这个值是在哪里被定义的. 而如果用 Config 来管理这个值, 你要改任何值都只需要到 Config 模块中去找即可.

    当这个值在代码库中用到了不止一次, 这就意味着你要改的时候要改很多地方. 这样很容易遗漏和出错.

    换言之, 凡是你在代码中 hard code 了任何值, 你都应该想想这个值以后可不可能变, 这个值会被引用一次还是多次.

- 用 ``config["key"]`` 这样的字典方式来访问 Config Value.

    用硬编码字符串作为 key 来访问值容易出现 Typo. 当 key 很长, 或者层级结构很复杂的时候人类很容易出错. 而如果用 Python 类来定义 Config 对象则可以利用 static check 实时发现 typo, 也可以利用 IDE 的自动补全功能提示来正确输入复杂的 key. 同时还能用 Type Hint 来提示这个 Config Value 的数据类型, 防止出错.

- 认为 Config 是数据而不是逻辑, 所以不对 Config 进行单元测试.

    诚然, 很多项目的单元测试中会间接引用到 Config 模块. 但 Config 模块的初始化往往发生在整个代码逻辑的最开始处. 我们应该对其进行测试, 以确保问题能够尽早的发现. 在 Config 模块的单元测试中我们应该尝试初始化 Config 对象, 换言之也就是读取 Config 数据. 然后把凡是要用到 Config 的引用都引用一遍. 如果有人更改了 Config, 只要运行单元测试就能知道这个改动是否会造成问题.


Config Management Best Practices
------------------------------------------------------------------------------
以上这些错误应当避免. 除此之外, 还有一些 Optional 的 Best Practices, 下面我们来一一介绍.

- Configuration as Code.

    对于不敏感的 Config, 应该将其视为代码的一部分, 用 Git 进行管理.

- Use AWS Parameter Store and Secret Manager to Store Configurations.

    90% 的情况下, AWS Parameter 都是用来储存 Config 数据的最佳选择. 免费, 性能高, 且自带版本控制. 而对于需要更高阶的权限控制, 或是隔一段时间就要自动更新的敏感数据, 例如数据库密码, 则可以用 AWS Secret Manager 来管理.

- Separate the Config Schema declaration and Config data loading in different modules.

    通常情况下, Config Schema 是不会变的, 而 Config 数据是会变的. 所以应该将 Config Schema 的定义和 Config 数据的加载分开. 这样可以对 Config 的 Definition 使用 Dummy Data 单独进行单元测试. 这也使得 Config Definition 的复用变得更加容易, 因为它不牵涉到跟具体项目绑定的 Loading 的逻辑.

- Config Loading Logic should be conditionally.

    在不同的情况下读取 Config 数据的方式应该是不同的. 例如对于本地开发而言, 本地的 Config 文件就是 Ground Truth. 而对于 App 而要, Config Storage (AWS Paramter Store / Secret Manager) 或是 Environment Variable 就是 Ground Truth. 所以 Config Loading Logic 代码应该是可以根据不同的情况来选择不同的加载方式. 只要成功 Load Config 对象, 之后的代码就不需要关心 Config 数据是从哪里来的, 只需要引用 Config 对象就可以了.



POC-style projects often have numerous hardcoded values, with some constant values being used multiple times. This pattern make projects difficult to maintain and prone to errors. In contrast, a production-ready project requires a centralized location to store all configurations. Once configurations are defined, we no longer allow hard-coded values and only reference configurations.

In this project, we use the ``multi environment json`` pattern defined in `config_patterns <https://github.com/MacHu-GWU/config_patterns-project>`_ Python library to manage the configuration. Please read the ``config_patterns`` documentation to learn more about this pattern.

Below are the list of important files related to config management::

    ${python_lib_name}/config # the root folder of the config management system source code
    ${python_lib_name}/config/define # config schema definition
    ${python_lib_name}/config/define/main.py # centralized config object, config fields are break down into sub-modules
    ${python_lib_name}/config/define/app.py # app related configs, e.g. app name, app artifacts S3 bucket
    ${python_lib_name}/config/define/lbd_deploy.py # Lambda function deployment related configs
    ${python_lib_name}/config/define/lbd_func.py # per Lambda function name, memory size, timeout configs
    ${python_lib_name}/config/load.py # config value initialization
    config/config.json # include the non-sensitive config data
    ${HOME}/.projects/simple_lambda/config-secret.json # include the sensitive config data, the ${HOME} is your user home directory
    tests/config/test_config_load.py # the unit test for config management, everytime you changed any of the config.json, or config/ modules, you should run this test

The ``${python_lib_name}/config`` Python module implemented the "configuration as code" pattern, let's walk through the folder structure to get better understanding.

- The ``define/main.py`` module defines the configuration data schema (field and value pairs).
    - To improve maintainability, we break down the long list of configuration fields into sub-modules.
    - There are two types of configuration values: constant values and derived values. Constant values are static values that are hardcoded in the ``config.json`` file, typically a string or an integer. Derived values are calculated dynamically based on one or more constant values.
- The ``load.py`` module defines how to read the configuration data from external storage.
    - On a developer's local laptop, the data is read from a ``config.json`` file.
    - During CI build runtime and AWS Lambda function runtime, the data is read from the AWS Parameter Store.

Below is the implementation of the ``init`` module:

.. literalinclude:: ../../../../simple_lambda/config/load.py
   :language: python
