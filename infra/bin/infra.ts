#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "@aws-cdk/core";
import { InfraStack } from "../lib/infra-stack";
import * as fs from "fs";
import * as os from "os";
import { randomBytes } from "crypto";
import { MonitoringStack } from "../lib/monitoring-stack";

export interface Config {
  prefix: string;
  env: string;
  email: string;
  githubKey: string;
}

let config: Config = {
  prefix:
    os.userInfo().username.toLowerCase() + "-" + randomBytes(3).toString("hex"),
  env: "dev",
  email: "747b13b7.groups.unsw.edu.au@apac.teams.ms",
  githubKey: "",
};
// crm-users-login domain name won't allow upper case letters

if (fs.existsSync(__dirname + "/../config.json")) {
  config = require(__dirname + "/../config.json");
  let cfgChanged = false;
  if (!config.env) {
    config.env = "dev";
    cfgChanged = true;
  }
  if (!config.email) {
    config.email = "747b13b7.groups.unsw.edu.au@apac.teams.ms";
    cfgChanged = true;
  }

  if (cfgChanged) {
    console.log("updating config to config.json");
    fs.writeFileSync(__dirname + "/../config.json", JSON.stringify(config));
  }

  if (!config.githubKey) {
    console.error("You need a github API key in order to create this stack.");
    process.exit(1);
  }
} else {
  console.log("writing config to config.json");
  fs.writeFileSync(__dirname + "/../config.json", JSON.stringify(config));
}

const app = new cdk.App();
new InfraStack(app, `${config.prefix}-infrastructure`, config);
new MonitoringStack(app, `${config.prefix}-monitoring`, config);
