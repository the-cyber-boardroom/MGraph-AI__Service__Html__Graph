from enum import Enum


class Enum__Service_Environment(str, Enum):
    aws_lambda = 'aws-lambda'
    local      = 'local'