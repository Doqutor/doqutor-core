#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { InfraStack } from '../lib/infra-stack';
import * as fs from 'fs';
import * as os from 'os';
import {randomBytes} from 'crypto';

let config: {prefix: String} = {prefix: os.userInfo().username + '-' + randomBytes(3).toString('hex')};

if (fs.existsSync(__dirname + '/../config.json')) {
    config = require(__dirname + '/../config.json');
} else {
    console.log('writing config to config.json');
    fs.writeFileSync(__dirname + '/../config.json', JSON.stringify(config));
}

const app = new cdk.App();
new InfraStack(app, `${config.prefix}-infrastructure`);
