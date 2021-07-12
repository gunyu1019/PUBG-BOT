class PUBGBOT(Exception):
    """PUBG BOT 모듈의 기본 예외 클래스입니다."""
    pass


class HTTPException(PUBGBOT):
    """.HTTPClient의 기본 예외 클래스입니다."""
    def __init__(self, response):
        self.response = response
        super().__init__(f"{response.reason} (상태코드: {response.status})")


class Unauthorized(HTTPException):
    """로그인이 실패되었을 때 발생합니다.."""
    pass


class NotFound(HTTPException):
    """유저를 찾지 못할때 발생합니다."""
    pass


class InternalServerError(HTTPException):
    """API 서버에서 문제가 발생 했을 때, 발생하는 예외입니다."""
    pass


class ServiceUnavailable(HTTPException):
    """API 서버가 점검 중일 때, 발생하는 예외입니다."""
    pass


class BadRequest(HTTPException):
    """알수 없는 오류가 발생 했을 때, 발생하는 예외입니다."""
    pass


class TooManyRequests(HTTPException):
    """너무 많은 요청이 들어 왔을 때, 발생하는 예외입니다."""
    pass


class Forbidden(HTTPException):
    """접근이 거부되었을 때, 발생하는 예외입니다."""
    pass


class UnsupportedMediaType(HTTPException):
    """지원하지 않는 미디어 형태일때, 발생하는 예외입니다."""
    pass