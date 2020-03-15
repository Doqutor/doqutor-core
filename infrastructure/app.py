#!/usr/bin/env python3

from aws_cdk import core
from infrastructure.infrastructure_stack import InfrastructureStack

app = core.App()
InfrastructureStack(app, "infrastructure-zeph", env={'region': 'ap-southeast-2'})

app.synth()
