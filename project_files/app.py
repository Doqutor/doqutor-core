#!/usr/bin/env python3

from aws_cdk import core

from db_stack.db_stack import Database_Stack

app = core.App()
Database_Stack(app, "database",
        env={'region': 'us-east-1'})

app.synth()
