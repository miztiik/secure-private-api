from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_logs as _logs
from aws_cdk import core

import os


class GlobalArgs:
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "secure-private-api"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_07_30"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class UnSecurePublicApiStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        stack_log_level: str,
        back_end_api_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Serverless Event Processor using Lambda):
        # Read Lambda Code):
        self.s1 = ""
        self.delimiter = self.s1
        self.s = self.delimiter
        try:
            with open("secure_private_api/stacks/back_end/lambda_src/serverless_greeter.py", mode="r") as f:
                unsecure_greeter_fn_code = f.read()
        except OSError as e:
            print("Unable to read Lambda Function Code")
            raise e

        unsecure_greeter_fn = _lambda.Function(
            self,
            "unSecureGreeterFn",
            function_name="unsecure_greeter_fn",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(unsecure_greeter_fn_code),
            timeout=core.Duration.seconds(15),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": f"{stack_log_level}",
                "Environment": "Production",
                "ANDON_CORD_PULLED": "False"
            }
        )
        unsecure_greeter_fn_version = unsecure_greeter_fn.latest_version
        unsecure_greeter_fn_version_alias = _lambda.Alias(
            self,
            "greeterFnAlias",
            alias_name="MystiqueAutomation",
            version=unsecure_greeter_fn_version
        )

        # Create Custom Loggroup
        # /aws/lambda/function-name
        unsecure_greeter_fn_lg = _logs.LogGroup(
            self,
            "squareFnLoggroup",
            log_group_name=f"/aws/lambda/{unsecure_greeter_fn.function_name}",
            retention=_logs.RetentionDays.ONE_WEEK,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # Add API GW front end for the Lambda
        back_end_01_api_stage_options = _apigw.StageOptions(
            stage_name="miztiik",
            throttling_rate_limit=10,
            throttling_burst_limit=100,
            logging_level=_apigw.MethodLoggingLevel.INFO
        )

        # Create API Gateway
        unsecure_public_api_01 = _apigw.RestApi(
            self,
            "backEnd01Api",
            rest_api_name=f"{back_end_api_name}",
            deploy_options=back_end_01_api_stage_options,
            endpoint_types=[
                _apigw.EndpointType.REGIONAL
            ]
        )

        back_end_01_api_res = unsecure_public_api_01.root.add_resource(
            "unsecure")
        greeter = back_end_01_api_res.add_resource("greeter")

        greeter_method_get = greeter.add_method(
            http_method="GET",
            request_parameters={
                "method.request.header.InvocationType": True,
                "method.request.path.number": True
            },
            integration=_apigw.LambdaIntegration(
                handler=unsecure_greeter_fn,
                proxy=True
            )
        )

        # Outputs
        output_1 = core.CfnOutput(
            self,
            "ApiUrl",
            value=f"{greeter.url}",
            description="Use a browser to access this url."
        )
