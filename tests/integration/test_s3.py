# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import time
import boto3.session

from tests import unittest


class TestS3Resource(unittest.TestCase):
    def setUp(self):
        # We use the us-east-1 region here to prevent needing
        # to set up special bucket configuration.
        self.session = boto3.session.Session(region_name='us-east-1')
        self.s3 = self.session.resource('s3')
        self.bucket_name = 'boto3-test-{0}'.format(int(time.time()))

    def test_s3(self):
        client = self.s3.meta['client']

        # Create a bucket (resource action with a resource response)
        bucket = self.s3.create_bucket(Bucket=self.bucket_name)
        waiter = client.get_waiter('bucket_exists')
        waiter.wait(Bucket=self.bucket_name)
        self.addCleanup(bucket.delete)

        # Create an object
        obj = bucket.Object('test.txt')
        obj.put(
            Body='hello, world')
        waiter = client.get_waiter('object_exists')
        waiter.wait(Bucket=self.bucket_name, Key='test.txt')
        self.addCleanup(obj.delete)

        # List objects and make sure ours is present
        self.assertIn('test.txt', [o.key for o in bucket.objects.all()])

        # Lazy-loaded attribute
        self.assertEqual(12, obj.content_length)

        # Perform a resource action with a low-level response
        self.assertEqual(b'hello, world',
                         obj.get()['Body'].read())
