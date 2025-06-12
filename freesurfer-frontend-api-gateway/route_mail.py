import boto3
import json
from botocore.exceptions import ClientError

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
SENDER = "<no-reply@domain.com>"

# Replace recipient@example.com with a "To" address. If your account 
# is still in the sandbox, this address must be verified.
RECIPIENT = "mail@domain.com"

# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the 
# ConfigurationSetName=CONFIGURATION_SET argument below.
# CONFIGURATION_SET = "ConfigSet"

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
AWS_REGION = "eu-central-1"

# The subject line for the email.
SUBJECT = "Amazon SES Test (SDK for Python)"

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
            )
            
# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Amazon SES Test (SDK for Python)</h1>
  <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    <a href='https://aws.amazon.com/sdk-for-python/'>
      AWS SDK for Python (Boto)</a>.</p>
</body>
</html>
            """            

# The character encoding for the email.
CHARSET = "UTF-8"



def sendConfirmationMail(user, email):
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        err_msg = e.response['Error']['Message']
        print("sendConfirmationMail error: ", err_msg)
        return {'error': err_msg}
    else:
        message_id = response['MessageId'] 
        print("Email sent! Message ID:", message_id)
        return {'success': str(message_id) }


def handlePOST(user, email, body):
    if not body:
        return {'error': 'body empty'}

    body_json = json.loads(body)
    action = body_json.get('action')
    if action == 'send':
        type = body_json.get('type')
        if type == 'confirm':
            return sendConfirmationMail(user, email)
        else:
            return {'error': 'wrong type'}
    else:
        return {'error:', 'wrong action'}

def handlePathMail(user, method, email, body):
    if method == 'POST':
        return handlePOST(user, email, body)
    else:
        return {'error': 'method not found'}

