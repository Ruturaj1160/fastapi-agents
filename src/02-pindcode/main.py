from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(
    title="PINCODE LOOKUP SERVICE",
    description="Autofill pincode and address details based on the input.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Pincode Lookup Service!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    print("Server started at http://localhost:8000")
