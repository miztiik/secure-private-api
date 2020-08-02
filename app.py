#!/usr/bin/env python3

from aws_cdk import core

from secure_private_api.stacks.back_end.vpc_stack import VpcStack
from secure_private_api.stacks.back_end.secure_private_api_stack import SecurePrivateApiStack
from secure_private_api.stacks.back_end.unsecure_public_api_stack import UnSecurePublicApiStack
from secure_private_api.stacks.back_end.api_consumer_stack import ApiConsumerStack


app = core.App()

# VPC Stack for hosting Secure API & Other resources
vpc_stack = VpcStack(
    app, "secure-private-api-vpc-stack",
    description="VPC Stack for hosting Secure API & Other resources"
)

# Deploy an unsecure public API
unsecure_public_api = UnSecurePublicApiStack(
    app,
    "unsecure-public-api",
    stack_log_level="INFO",
    back_end_api_name="unsecure_public_api_01",
    description="Deploy an unsecure public API"
)

# Secure your API by create private EndPoint to make it accessible from your VPCs
secure_private_api = SecurePrivateApiStack(
    app,
    "secure-private-api",
    vpc=vpc_stack.vpc,
    stack_log_level="INFO",
    back_end_api_name="secure_private_api_01",
    description="Secure your API by create private EndPoint to make it accessible from your VPCs"
)

# Launch an EC2 Instance in a given VPC
api_consumer_stack = ApiConsumerStack(
    app,
    "api-consumer",
    vpc=vpc_stack.vpc,
    api_sec_grp=secure_private_api.secure_private_api_01_sec_grp,
    stack_log_level="INFO",
    description="Launch an EC2 Instance in a given VPC"
)

# Stack Level Tagging
core.Tag.add(app, key="Owner",
             value=app.node.try_get_context('owner'))
core.Tag.add(app, key="OwnerProfile",
             value=app.node.try_get_context('github_profile'))
core.Tag.add(app, key="GithubRepo",
             value=app.node.try_get_context('github_repo_url'))
core.Tag.add(app, key="Udemy",
             value=app.node.try_get_context('udemy_profile'))
core.Tag.add(app, key="SkillShare",
             value=app.node.try_get_context('skill_profile'))
core.Tag.add(app, key="AboutMe",
             value=app.node.try_get_context('about_me'))


app.synth()
