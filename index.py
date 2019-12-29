"""
  Licensed under the Apache License, Version 2.0 (the "License").
  You may not use this file except in compliance with the License.
  A copy of the License is located at
      http://www.apache.org/licenses/LICENSE-2.0
  or in the "license" file accompanying this file. This file is distributed
  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied. See the License for the specific language governing
  permissions and limitations under the License.
"""

import os
import logging
import broker
import webhook

_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG if os.getenv('APP_DEBUG', '') == 'true' else logging.INFO)


def handler(event, context):

    _logger.debug(event)
    to_return = None

    if event['httpMethod'] == 'GET':
        to_return = broker.handler(event, context)
    elif event['httpMethod'] == 'POST':
        to_return = webhook.handler(event, context)

    if to_return is None:
        to_return = {
            'headers': {'Content-Type': 'application/json'},
            'statusCode': 503,
            'body': {'data': {'output': 'Invalid invocation'}}
        }

    return to_return


if __name__ == "__main__":
    print(handler({'httpMethod': 'GET', 'headers': {'Authorization': os.getenv('AUTH_TOKEN')}}, None))
