from pydantic import BaseModel


class SalesResponse(BaseModel):

    sku_id: str

    category: str

    channel: str

    date: str

    actual_sales_qty: float

    class Config:
        from_attributes = True