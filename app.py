#!/usr/bin/env python3

from aws_cdk import core

from secure_private_api.secure_private_api_stack import SecurePrivateApiStack


app = core.App()
SecurePrivateApiStack(app, "secure-private-api")

app.synth()
