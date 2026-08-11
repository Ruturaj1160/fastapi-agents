from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(
    title="Swiggy order service",
    description="This is a sample FastAPI application.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/about")
async def read_about():
    return {"about": "This is a sample FastAPI application."}


@app.get("/orders")
def list_orders():
    """List recernt orders"""
    return {
        "orders": [
            {"id": 1, "item": "Butter Chicken", "status": "delivered"},
            {"id": 2, "item": "Masala Dosa", "status": "preparing"},
            {"id": 3, "item": "Paneer Tikka", "status": "delivered"},
        ]
    }


@app.get("/orders/status")
def order_status():
    """Get order status"""
    return {"total_today": 2_340_23, "top_city": "Bengaluru"}


@app.get("/debug/request-info")
async def request_info(request: Request):
    """Inspect the raw request object"""
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "path_params": request.path_params,
        "query_params": dict(request.query_params),
    }


@app.get(
    "/orders/active",
    summary="Get Active Orders",
    description=(
        "Returns all orders that are currently being prepared" "or are out for delivery"
    ),
    tags=["orders"],
    response_description="List of active order objects",
    deprecated=False,
)
def get_active_order():
    """This docstring also apprears in docs"""
    return {
        "active_orders": [
            {"id": 1, "item": "Masala Dosa", "status": "out_for_delivery"}
        ]
    }


@app.get("/restaurants", tags=["restaurants"])
def list_restaurants():
    """List all restaurants"""
    return {
        "restaurants": [
            {"id": 1, "name": "Biryani House", "cuisine": "Indian"},
            {"id": 2, "name": "Pizza Palace", "cuisine": "Italian"},
            {"id": 3, "name": "Sushi World", "cuisine": "Japanese"},
        ]
    }


@app.get("/restaurants/delhi", tags=["restaurants"])
def list_delhi_restaurants():
    """List all restaurants in Delhi"""
    return {
        "restaurants": [
            {"id": 1, "name": "Biryani House", "cuisine": "Indian"},
            {"id": 2, "name": "Pizza Palace", "cuisine": "Italian"},
            {"id": 3, "name": "Sushi World", "cuisine": "Japanese"},
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
