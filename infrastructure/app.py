#!/usr/bin/env python3

from aws_cdk import core
from infrastructure.stack import InfrastructureStack
from config import get_config

# fix for multiple people trying to deploy

cfg = get_config()

app = core.App()
InfrastructureStack(app, f"{cfg['prefix']}-infrastructure", env={'region': 'ap-southeast-2'})

app.synth()
