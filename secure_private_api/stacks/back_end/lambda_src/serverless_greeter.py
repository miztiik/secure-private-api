# -*- coding: utf-8 -*-


import json
import logging
import os
from botocore.vendored import requests


class global_args:
    """ Global statics """
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    MODULE_NAME = "greeter_lambda"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    ANDON_CORD_PULLED = False


def set_logging(lv=global_args.LOG_LEVEL):
    """ Helper to enable logging """
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


# Initial some defaults in global context to reduce lambda start time, when re-using container
logger = set_logging(logging.INFO)


def _get_lambda_ip():
    ip = ""
    try:
        ip = requests.get(
            "http://checkip.amazonaws.com").text.replace("\n", "")
    except requests.RequestException as e:
        raise e
    return ip


def lambda_handler(event, context):
    logger.debug(f"recvd_event:{event}")
    ip = _get_lambda_ip()
    return {
        "statusCode": 200,
        "body": f'{{"message": "Hi Miztikal World, Hello from Lambda running at {ip}"}}'
    }
