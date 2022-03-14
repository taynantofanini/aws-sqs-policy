import boto3
import json

client = boto3.client('sqs')

def list_sqs_urls():
    response = client.list_queues()["QueueUrls"]
    #print(response)
    return response

def get_queue_attributes(sqs_list):
    for url in sqs_list:
        attributes = client.get_queue_attributes(QueueUrl=url, AttributeNames=['Policy','QueueArn'])["Attributes"]
        compare_queue_policy(attributes,url)

def compare_queue_policy(attributes, url):
    statement = {
        "Sid": "Sid01234567890",
        "Effect": "Deny",
        "Principal": {
            "AWS": "arn:aws:iam::049317870295:root"
        },
        "Action": "SQS:*",
        "Resource": attributes["QueueArn"],
        "Condition": {
            "Bool": {
            "aws:SecureTransport": "false"
            }
        }
        }
    if "Policy" in attributes:
        policy = attributes["Policy"]
        policy = json.loads(policy)
        if statement not in policy["Statement"]:
            att_queue_policy(url, policy, statement, attributes)
        else:
            print("O SQS de arn '{}' não precisa ser atualizado".format(attributes["QueueArn"]))
    else:
        put_sqs_policy(url, attributes)

def att_queue_policy(url, policy, statement, attributes):
    new_policy = policy
    new_policy["Statement"].append(statement)
    new_policy = json.dumps(new_policy)
    response = client.set_queue_attributes(QueueUrl=url, Attributes={'Policy': new_policy})
    print("O SQS de arn '{}' foi atualizado".format(attributes["QueueArn"]))

def put_sqs_policy(url, attributes):
    new_policy = json.dumps(
    {
    "Version": "2012-10-17",
    "Id": attributes["QueueArn"],
    "Statement": [
        {
        "Sid": "Sid01234567890",
        "Effect": "Deny",
        "Principal": {
            "AWS": "arn:aws:iam::049317870295:root"
        },
        "Action": "SQS:*",
        "Resource": attributes["QueueArn"],
        "Condition": {
            "Bool": {
            "aws:SecureTransport": "false"
            }
        }
        }
    ]
    }
    )
    #policy = '{"Version": "2012-10-17","Statement": [{"Sid": "Sid01234567890","Effect": "Deny","Principal": {"AWS": "arn:aws:iam::049317870295:root"},"Action": "SQS:","Resource":"' + attributes["QueueArn"] + '","Condition": {"Bool": {"aws:SecureTransport": "false"} } }]}'
    response = client.set_queue_attributes(QueueUrl=url, Attributes={'Policy': new_policy})
    print("O SQS de arn '{}' não possuía policy e ela foi adicionada".format(attributes["QueueArn"]))

if __name__ == "__main__":
    #sqs_list = list_sqs_urls()
    sqs_list = ["https://sqs.us-east-1.amazonaws.com/049317870295/lab-taynan"]
    get_queue_attributes(sqs_list)

