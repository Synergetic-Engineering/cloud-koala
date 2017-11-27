# XXX need to set these environment variables before importing handler/lib
# Figure there'll be a better way to do this once we use moto?
import os
# XXX - shouldn't actually be deployed resources, the should be mock ones using moto
os.environ['DYNAMODB_TABLE'] = 'cloud-koala-dev-models'
os.environ['S3_BUCKET'] = 'cloud-koala-dev-models'
