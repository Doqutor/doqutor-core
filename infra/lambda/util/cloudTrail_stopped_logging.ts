import * as cloudTrail from "aws-sdk/clients/cloudtrail";
import * as lambda from "@aws-cdk/aws-lambda";

export const handler = async (event: any = {}): Promise<any> => {
  console.log(event);
  const client = new cloudTrail();
  const eventName = event["detail"]["eventName"];
  const cloudTrailParams: cloudTrail.StartLoggingRequest = {
    Name: event["detail"]["requestParameters"]["name"],
  };
  console.log(
    "trying to start log==========" +
      event["detail"]["requestParameters"]["name"]
  );
  console.log(cloudTrailParams);
  client.startLogging(cloudTrailParams);

  const userName = event["detail"]["userIdentity"]["userName"];
  const eventTime = event["detail"]["eventTime"];
  const sourceIPAddress = event["detail"]["sourceIPAddress"];
  console.log(userName, eventTime, eventName, sourceIPAddress);

  return { statusCode: 201, body: "Hello world!" };
};
