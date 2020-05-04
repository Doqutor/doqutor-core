import * as cdk from '@aws-cdk/core';
import { StaticWebsiteStack, IStaticWebsiteProps } from 'aws-cdk-static-website';

export class WebStack extends StaticWebsiteStack {
  constructor(scope: cdk.App, id: string) {
    const props: IStaticWebsiteProps = {
      websiteDistPath: './dist',
      deploymentVersion: '1.0.0',
      resourcePrefix: 'my-web-stack',
      indexDocument: 'index.html',
    };

    super(scope, id, props);
  }
}