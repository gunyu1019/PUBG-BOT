class RequestsModel:
    def __init__(self, response):
        self.status = response.get('status')
        self.data = response.get('data')
        self.version = response.get('version')
        self.content_type = response.get('content-type')
        self.reason = response.get('reason')
