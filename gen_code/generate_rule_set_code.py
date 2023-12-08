# -*- coding: utf-8 -*-

import aws_ops_alpha.workflow.simple_python.api as simple_python
import aws_ops_alpha.workflow.simple_lambda.api as simple_lambda

simple_python.rule_set.generate_code()
simple_lambda.rule_set.generate_code()
