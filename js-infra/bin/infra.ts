#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { InfraStack } from '../lib/infra-stack';
import * as fs from 'fs';
import * as os from 'os';
import {randomBytes} from 'crypto';
import { MonitoringStack } from '../lib/monitoring-stack';

let config: {prefix: String, env: string} = {prefix: os.userInfo().username.toLowerCase() + '-' + randomBytes(3).toString('hex'), env: 'dev'};
// crm-users-login domain name won't allow upper case letters

if (fs.existsSync(__dirname + '/../config.json')) {
    config = require(__dirname + '/../config.json');
    if (!config.env) {
        config.env = 'dev';
        console.log('updating config to config.json');
        fs.writeFileSync(__dirname + '/../config.json', JSON.stringify(config));
    }
} else {
    console.log('writing config to config.json');
    fs.writeFileSync(__dirname + '/../config.json', JSON.stringify(config));
}

const app = new cdk.App();
new InfraStack(app, `${config.prefix}-infrastructure`, undefined, config.env);
new MonitoringStack(app, `${config.prefix}-monitoring`);