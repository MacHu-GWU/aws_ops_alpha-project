# -*- coding: utf-8 -*-

import typing as T
import importlib
import dataclasses

from pathlib_mate import Path
from rstobj import ListTable
from tt4human.api import TruthTable

from aws_ops_alpha.paths import dir_python_lib


def to_list_table(name: str, truth_table: TruthTable) -> ListTable:
    data = [truth_table.headers]
    for row in truth_table.rows:
        data.append([str(i) for i in row])
    return ListTable(
        data=data,
        title=name,
        header=True,
    )


@dataclasses.dataclass
class Project:
    project_type: str
    truth_table_list_table: ListTable

truth_table_list_table_list = list()
project_list = list()
for project_type in [
    "simple_python",
    "simple_config",
    "simple_cdk",
    "simple_lambda",
    "simple_lbd_agw_chalice",
    "simple_lbd_container",
    "simple_glue",
]:
    module = importlib.import_module(f"aws_ops_alpha.project.{project_type}.{project_type}_truth_table")
    list_table = to_list_table(project_type, module.truth_table)
    project_list.append(Project(
        project_type=project_type,
        truth_table_list_table=list_table,
    ))

# fmt: off
doc_data = dict(
    project_list=project_list,
)
# fmt: on
