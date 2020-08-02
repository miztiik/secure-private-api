from aws_cdk import aws_ec2 as _ec2
from aws_cdk import core


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


class VpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, from_vpc_name=None, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        if from_vpc_name is not None:
            self.vpc = _ec2.Vpc.from_lookup(
                self, "vpc",
                vpc_name=from_vpc_name
            )
        else:
            self.vpc = _ec2.Vpc(
                self,
                "miztiikVpc",
                cidr="10.10.0.0/16",
                max_azs=2,
                nat_gateways=0,
                subnet_configuration=[
                    _ec2.SubnetConfiguration(
                        name="public", cidr_mask=24, subnet_type=_ec2.SubnetType.PUBLIC
                    ),
                    # _ec2.SubnetConfiguration(
                    #     name="app", cidr_mask=24, subnet_type=_ec2.SubnetType.PRIVATE
                    # ),
                    _ec2.SubnetConfiguration(
                        name="db", cidr_mask=24, subnet_type=_ec2.SubnetType.ISOLATED
                    )
                ]
            )

        output_0 = core.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )
        output_1 = core.CfnOutput(
            self,
            "VpcId",
            value=self.vpc.vpc_id,
            export_name="VpcId")
