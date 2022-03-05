import logging
import requests

from uuid import uuid4


class ThirdPartyService():
    logger = logging.getLogger(__name__)

    def call(
            self,
            method,
            url,
            payload,
            headers=None,
            auth=None,
            timeout=None,
    ) -> requests.Response:
        if not headers:
            headers = {}

        headers['X-Request-ID'] = str(uuid4())

        self.logger.info(
            f'Requesting API {method} {url}',
            extra={
                'request': {
                    'data': payload,
                    'headers': headers,
                    'method': method,
                    'url': url,
                },
            }
        )

        try:
            response = requests.request(
                method,
                url,
                data=payload,
                headers=headers,
                auth=auth,
                timeout=timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exception:
            status_code = None
            response_data = None
            if exception.response:
                status_code = exception.response.status_code
                response_data = {
                    'headers': exception.response.headers,
                    'status_code': exception.response.status_code,
                    'text': exception.response.text,
                }

            self.logger.warning(
                f'API responded {status_code} {method} {url}',
                exc_info=True,
                extra={
                    'request': {
                        'headers': headers,
                        'method': method,
                        'url': url,
                    },
                    'response': response_data,
                },
            )

            raise exception

        self.logger.info(
            f'API responded {response.status_code} {method} {url}',
            extra={
                'request': {
                    'headers': headers,
                    'method': method,
                    'url': url,
                },
                'response': {
                    'headers': response.headers,
                    'status_code': response.status_code,
                    'text': response.text,
                },
            },
        )

        return response
