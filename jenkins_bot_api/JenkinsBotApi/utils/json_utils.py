"""
@author: Sukan Singh
@Description: Json Utility
"""
import json
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse


def fetch_value_by_jsonPath(jsonPayload, jsonPath):
    jsonPathExpr = parse(jsonPath)
    result = jsonPathExpr.find(jsonPayload)
    result_list = list()
    for i in result:
        result_list.append(i.value)
    return result_list
