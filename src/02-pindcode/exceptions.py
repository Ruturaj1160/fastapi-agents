# custom exception classes for the Pindcode project
from fastapi.responses import JSONResponse
from fastapi import Request


class PincodeNotFoundException(Exception):

    # dunder - to initialize the class
    def __init__(self, pincode: str):
        self.pincode = pincode
        # why we are doing it this way is because we want to return a custom message when the exception is raised


class InvalidPincodeException(Exception):
    def __init__(
        self,
        pincode: str,
        reason: str = "Invalid pincode format. Pincode must be a 6-digit number.",
    ):
        self.pincode = pincode
        self.reason = reason


# custom exception handler for PincodeNotFoundException
async def pincode_not_found_exception_handler(
    request: Request, exc: PincodeNotFoundException
):
    return JSONResponse(
        status_code=404,
        content={
            "message": f"Pincode {exc.pincode} not found in the database.",
            "status": "error",
            "pincode": exc.pincode,
        },
    )


# custom exception handler for InvalidPincodeException
async def invalid_pincode_exception_handler(
    request: Request, exc: InvalidPincodeException
):
    return JSONResponse(
        status_code=400,
        content={
            "message": f"Invalid pincode {exc.pincode}. {exc.reason}",
            "status": "error",
            "pincode": exc.pincode,
            "reason": exc.reason,
        },
    )
