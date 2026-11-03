from pydantic import BaseModel, ConfigDict, Field


class MonobankWebhookIn(BaseModel):
    """Only the invoice id is read; the status is re-checked with the bank."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    invoice_id: str = Field(alias="invoiceId", min_length=1, max_length=64)


class WebhookAckOut(BaseModel):
    ok: bool = True
