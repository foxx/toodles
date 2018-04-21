"""Exception classes of this library"""

__all__ = ['BaseError', 'ClientError', 'BadRequestError', 'RequestSchemaError',
           'NotAuthenticatedError', 'NotAuthorizedError', 'ServerError',
           'ResponseSchemaError']


###############################################################################
# WSGI related exceptions
###############################################################################

class BaseError(Exception):
    """Base exception class"""

    status_code = None
    error_code = None
    error_desc = None
    error_detail = None
    original_exc = None

    def __init__(self, status_code:int=None, error_code:str=None, 
                 error_desc:str=None, error_detail=None,
                 original_exc:Exception=None):
        super().__init__(self)

        if status_code is not None: 
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        if error_desc is not None:
            self.error_desc = error_desc
        if error_detail is not None:
            self.error_detail = error_detail
        if original_exc is not None:
            self.original_exc = original_exc

    def __str__(self):
        return "[status_code={}, code={}, desc={}, detail={}]".format(
            self.status_code, self.error_code, self.error_desc,
            self.error_detail)

    def to_dict(self):
        return dict(error_code=self.error_code,
                    error_desc=self.error_desc,
                    status_code=self.status_code,
                    error_detail=self.error_detail)


###############################################################################
# Client exceptions
###############################################################################

class ClientError(BaseError):
    """Base exception for all client errors"""
    status_code = 400
    error_code = "bad_request"
    error_desc = "There was an unknown problem with your request"


class BadRequestError(ClientError):
    status_code = 400
    error_code = "bad_request"
    error_desc = "Request was not properly formed"


class RequestSchemaError(ClientError):
    """Request schema was invalid"""
    status_code = 400
    error_code = "bad_request"
    error_desc = "Request payload does not match schema"


class NotAuthenticatedError(ClientError):
    """Request was invalid"""
    status_code = 401
    error_code = "auth_error"
    error_desc = "Client authentication failed"


class NotAuthorizedError(ClientError):
    """Request was invalid"""
    status_code = 403
    error_code = "auth_error"
    error_desc = "Client has insufficient authorization"


###############################################################################
# Server exceptions
###############################################################################

class ServerError(BaseError):
    """Base exception for all server errors"""
    status_code = 500
    error_code = "server_error"
    error_desc = "There was a server error, please try again later"


class ResponseSchemaError(ServerError):
    """Response schema was invalid"""



