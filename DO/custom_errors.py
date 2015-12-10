# -*- coding: utf-8 -*-
from werkzeug.exceptions import HTTPException


class CustomError(HTTPException):
    """
    Custom error for Restful Flask
    """
    code = 500
    description = (
        'This server is a teapot, not a coffee machine, also developer forgot totally to add description for this Error message.'
    )

    def __init__(self, description="Server encountered internal error", code=500):
        self.description = description
        self.code = code
