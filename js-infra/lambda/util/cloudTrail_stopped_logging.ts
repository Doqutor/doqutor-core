import * as cloudTrail from 'aws-sdk/clients/cloudtrail';
import * as lambda from '@aws-cdk/aws-lambda';
// TODO:
// CodePipelineCloudWatchEvent
// https://github.com/DefinitelyTyped/DefinitelyTyped/blob/56c1ea26b59ed0e4634b1ba27096ab3b90371875/types/aws-lambda/index.d.ts#L211
export const handler = async (event: any = {}) : Promise <any> => {
  console.log('this is the log to tell that we have really logged things');
  console.log(event);
  const c = new cloudTrail({
    endpoint: `https://${event['source'].split('.')[1]}.${event['region']}.amazonaws.com`
  });

  const cloudTrailParams: cloudTrail.StartLoggingRequest = {
    Name: event['detail']['requestParameters']['name']
  };
  console.log('trying to start log');
  c.startLogging(cloudTrailParams);

  const userName = event['detail']['userIdentity']['userName'];
  const eventTime = event['detail']['eventTime'];
  const eventName = event['detail']['eventName'];
  const sourceIPAddress = event['detail']['sourceIPAddress'];
  console.log(userName, eventTime, eventName, sourceIPAddress);

  return { statusCode: 201, body: 'Hello world!' };
};
