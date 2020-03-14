#!/usr/bin/env python3

from aws_cdk import core

from db_stack.db_stack import Database_Stack
from cognito_stack.cognito_stack import Cognito_Stack

app = core.App()
Database_Stack(app, "database",
        env={'region': 'us-east-1'})

#Cognito_Stack(app, "database",
#        env={'region': 'us-east-1'})

app.synth()
