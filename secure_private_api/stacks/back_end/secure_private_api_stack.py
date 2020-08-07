from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_logs as _logs
from aws_cdk import aws_ec2 as _ec2
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


class SecurePrivateApiStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        vpc,
        stack_log_level: str,
        back_end_api_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Serverless Event Processor using Lambda):
        # Read Lambda Code):
        try:
            with open("secure_private_api/stacks/back_end/lambda_src/serverless_greeter.py", mode="r") as f:
                greeter_fn_code = f.read()
        except OSError as e:
            print("Unable to read Lambda Function Code")
            raise e

        greeter_fn = _lambda.Function(
            self,
            "getSquareFn",
            function_name=f"greeter_fn_{id}",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="index.lambda_handler",
            code=_lambda.InlineCode(greeter_fn_code),
            timeout=core.Duration.seconds(15),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": f"{stack_log_level}",
                "Environment": "Production",
                "ANDON_CORD_PULLED": "False"
            }
        )
        greeter_fn_version = greeter_fn.latest_version
        greeter_fn_version_alias = _lambda.Alias(
            self,
            "greeterFnAlias",
            alias_name="MystiqueAutomation",
            version=greeter_fn_version
        )

        # Create Custom Loggroup
        # /aws/lambda/function-name
        greeter_fn_lg = _logs.LogGroup(
            self,
            "squareFnLoggroup",
            log_group_name=f"/aws/lambda/{greeter_fn.function_name}",
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

        # Lets create a private secure end point

        # Create a security group dedicated to our API Endpoint
        self.secure_private_api_01_sec_grp = _ec2.SecurityGroup(
            self,
            "secureApi01SecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
            description="Miztiik Automation: Secure our private API using security groups"
        )

        # Allow 443 inbound on our Security Group
        self.secure_private_api_01_sec_grp.add_ingress_rule(
            _ec2.Peer.ipv4(vpc.vpc_cidr_block),
            _ec2.Port.tcp(443)
        )

        secure_private_api_01_endpoint = _ec2.InterfaceVpcEndpoint(
            self,
            "secureApi01Endpoint",
            vpc=vpc,
            service=_ec2.InterfaceVpcEndpointAwsService.APIGATEWAY,
            private_dns_enabled=True,
            subnets=_ec2.SubnetSelection(
                subnet_type=_ec2.SubnetType.ISOLATED
            )
        )

        # Create a API Gateway Resource Policy to attach to API GW
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-policy
        secure_private_api_01_res_policy = _iam.PolicyDocument(
            statements=[
                _iam.PolicyStatement(
                    principals=[_iam.AnyPrincipal()],
                    actions=["execute-api:Invoke"],
                    # resources=[f"{api_01.arn_for_execute_api(method="GET",path="greeter", stage="miztiik")}"],
                    resources=[core.Fn.join("", ["execute-api:/", "*"])],
                    effect=_iam.Effect.DENY,
                    conditions={
                        "StringNotEquals":
                        {
                            "aws:sourceVpc": f"{secure_private_api_01_endpoint.vpc_endpoint_id}"
                        }
                    },
                    sid="DenyAllNonVPCAccessToApi"
                ),
                _iam.PolicyStatement(
                    principals=[_iam.AnyPrincipal()],
                    actions=["execute-api:Invoke"],
                    resources=[core.Fn.join("", ["execute-api:/", "*"])],
                    effect=_iam.Effect.ALLOW,
                    sid="AllowVPCAccessToApi"
                )
            ]
        )

        # Create API Gateway
        secure_private_api_01 = _apigw.RestApi(
            self,
            "backEnd01Api",
            rest_api_name=f"{back_end_api_name}",
            deploy_options=back_end_01_api_stage_options,
            endpoint_types=[
                _apigw.EndpointType.PRIVATE
            ],
            policy=secure_private_api_01_res_policy,
        )

        back_end_01_api_res = secure_private_api_01.root.add_resource("secure")
        greeter = back_end_01_api_res.add_resource("greeter")

        greeter_method_get = greeter.add_method(
            http_method="GET",
            request_parameters={
                "method.request.header.InvocationType": True,
                "method.request.path.number": True
            },
            integration=_apigw.LambdaIntegration(
                handler=greeter_fn,
                proxy=True
            )
        )

        # Outputs
        output_1 = core.CfnOutput(
            self,
            "SecureApiUrl",
            value=f"{greeter.url}",
            description="Use an utility like curl from the same VPC as the API to invoke it."
        )
