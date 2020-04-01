export const handler = async (event: any = {}) : Promise <any> => {
  console.log('this is the log to tell that we have really logged things');
  console.log(event);

  return { statusCode: 201, body: 'Hello world!' };
};
