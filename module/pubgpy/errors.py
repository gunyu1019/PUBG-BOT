"""
MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class APIException(Exception):
    """Exception occurred while communicating with API."""
    def __init__(self, response, message):
        self.response = response
        if isinstance(message, dict):
            self.text = message.get('title', '')
        else:
            self.text = message
        if self.text != '':
            super().__init__("{} (Status Code: {}): ".format(self.text, response.status))
        else:
            super().__init__("(Status Code: {})".format(response.status))


class Unauthorized(APIException):
    """Unauthorized"""
    pass


class NotFound(APIException):
    """Not Found"""
    pass


class UnsupportedMediaType(APIException):
    """Unsupported Media Type"""
    pass


class TooManyRequests(APIException):
    """Too Many Requests"""
    pass
