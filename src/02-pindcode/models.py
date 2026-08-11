from pydantic import BaseModel, Field, field_validator


class PincodeRequest(BaseModel):
    pincode: str

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value):
        if not value.isdigit() or len(value) != 6:
            raise ValueError("Pincode must be a 6-digit number.")
        return value


class LocationResponse(BaseModel):
    pincode: str
    city: str
    state: str
    district: str


class BulkPincodeRequest(BaseModel):
    pincodes: list[str] = Field(..., min_items=1, max_items=20)

    @field_validator("pincodes")
    @classmethod
    def validate_pincodes(cls, values):
        if len(values) > 20:
            raise ValueError("You can only request up to 20 pincodes at a time.")
        if len(values) < 1:
            raise ValueError("You must provide at least one pincode.")
        if len(values) != len(set(values)):
            raise ValueError("Duplicate pincodes are not allowed.")
        for pincode in values:
            if not pincode.isdigit() or len(pincode) != 6:
                raise ValueError(f"Pincode {pincode} must be a 6-digit number.")
        return values


class BulkResponse(BaseModel):
    status: str = "success"
    found: int

    not_found: int
    results: list[LocationResponse] = Field(default_factory=list)

    missing: list[str]
