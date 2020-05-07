import {
  expect as expectCDK,
  matchTemplate,
  MatchStyle,
} from "@aws-cdk/assert";
import * as cdk from "@aws-cdk/core";
import JsInfra = require("../lib/infra-stack");
import { Config } from "../bin/infra";
import * as os from "os";
import { randomBytes } from "crypto";

test("Empty Stack", () => {
  const app = new cdk.App();
  let config: Config = {
    prefix:
      os.userInfo().username.toLowerCase() +
      "-" +
      randomBytes(3).toString("hex"),
    env: "test",
    email: "yourNotificationChannel.com",
    githubKey: "somekey"
  };
  // WHEN
  const stack = new JsInfra.InfraStack(app, "MyTestStack", config, {});
  // THEN
  expectCDK(stack).to(
    matchTemplate(
      {
        Resources: {},
      },
      MatchStyle.EXACT
    )
  );
});
