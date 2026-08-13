from fastapi import FastAPI, Request
import uvicorn
from exceptions import (
    PincodeNotFoundException,
    InvalidPincodeException,
    pincode_not_found_exception_handler,
    invalid_pincode_exception_handler,
)
from data import pincode_db

from models import PincodeRequest, LocationResponse, BulkPincodeRequest, BulkResponse

app = FastAPI(
    title="PINCODE LOOKUP SERVICE",
    description="Autofill pincode and address details based on the input.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# register custom exception handlers
# takes two arguments, the exception class and the handler function
app.add_exception_handler(PincodeNotFoundException, pincode_not_found_exception_handler)
app.add_exception_handler(InvalidPincodeException, invalid_pincode_exception_handler)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Pincode Lookup Service!"}


@app.get("/pincode/{code}", response_model=LocationResponse)
def get_pincode(code: str):

    if len(code) != 6 or not code.isdigit():
        raise InvalidPincodeException(code)

    if code not in pincode_db:
        raise PincodeNotFoundException(code)

    code_data = pincode_db[code]

    if not code_data:
        raise PincodeNotFoundException(code)

    return LocationResponse(
        pincode=code_data["pincode"],
        city=code_data["city"],
        state=code_data["state"],
        district=code_data["district"],
    )


@app.post("/pincode/bulk", response_model=BulkResponse)
def get_bulk_pincode(request: BulkPincodeRequest):
    pincodes = request.pincodes
    found_results = []
    missing_pincodes = []

    for code in pincodes:
        if len(code) != 6 or not code.isdigit():
            raise InvalidPincodeException(code)

        if code in pincode_db:
            code_data = pincode_db[code]
            found_results.append(
                LocationResponse(
                    pincode=code_data["pincode"],
                    city=code_data["city"],
                    state=code_data["state"],
                    district=code_data["district"],
                )
            )
        else:
            missing_pincodes.append(code)

    return BulkResponse(
        found=len(found_results),
        not_found=len(missing_pincodes),
        results=found_results,
        missing=missing_pincodes,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    print("Server started at http://localhost:8000")
