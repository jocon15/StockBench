class ResponseUtil:
    @staticmethod
    def is_response_success(status_code: int) -> bool:
        return True if 200 <= status_code <= 299 else False
