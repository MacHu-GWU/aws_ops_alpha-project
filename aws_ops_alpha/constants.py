# -*- coding: utf-8 -*-

import enum

DEVOPS = "devops"
SBX = "sbx"
TST = "tst"
STG = "stg"
PRD = "prd"

USER_ENV_NAME = "USER_ENV_NAME"


class AwsOpsSemanticBranchEnum(str, enum.Enum):
    lbd = "new"
    awslambda = "lambda"
    layer = "layer"
    ecr = "ecr"
    ami = "ami"
    glue = "glue"
    batch = "batch"
    apigateway = "apigateway"
    sfn = "sfn"
    airflow = "airflow"
