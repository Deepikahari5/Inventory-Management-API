from fastapi import FastAPI

from app.routers import categories, products, suppliers

app = FastAPI(
    title="Inventory Management API",
    description="Inventory API with Alembic-managed MySQL migrations",
    version="2.0.0",
)

app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(products.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Inventory Management API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
