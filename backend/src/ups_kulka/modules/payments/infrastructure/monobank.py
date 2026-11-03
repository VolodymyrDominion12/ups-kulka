"""monobank acquiring adapter (https://monobank.ua/api-docs/acquiring)."""

import httpx

from ups_kulka.modules.payments.application.dto import Invoice
from ups_kulka.modules.payments.application.ports import PaymentGateway
from ups_kulka.modules.payments.domain.entities import Payment, PaymentStatus

MONOBANK_API = "https://api.monobank.ua/api/merchant"
UAH = 980

STATUS_MAP: dict[str, PaymentStatus] = {
    "created": PaymentStatus.PENDING,
    "processing": PaymentStatus.PENDING,
    "hold": PaymentStatus.PENDING,
    "success": PaymentStatus.PAID,
    "failure": PaymentStatus.FAILED,
    "expired": PaymentStatus.FAILED,
    "reversed": PaymentStatus.REFUNDED,
}


class MonobankGateway:
    provider = "monobank"

    def __init__(self, token: str, public_base_url: str, timeout: float = 10.0) -> None:
        self._headers = {"X-Token": token}
        self._base_url = public_base_url.rstrip("/")
        self._timeout = timeout

    async def create_invoice(self, payment: Payment, description: str) -> Invoice:
        body = {
            "amount": payment.amount.kopecks,
            "ccy": UAH,
            "merchantPaymInfo": {
                "reference": str(payment.order_number),
                "destination": description,
            },
            "redirectUrl": f"{self._base_url}/diakuiemo?order={payment.order_number}",
            "webHookUrl": f"{self._base_url}/api/v1/payments/monobank/webhook",
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{MONOBANK_API}/invoice/create", json=body, headers=self._headers
            )
            response.raise_for_status()
            data = response.json()
        return Invoice(invoice_id=data["invoiceId"], page_url=data["pageUrl"])

    async def fetch_status(self, invoice_id: str) -> PaymentStatus:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{MONOBANK_API}/invoice/status",
                params={"invoiceId": invoice_id},
                headers=self._headers,
            )
            response.raise_for_status()
            status = response.json().get("status", "")
        return STATUS_MAP.get(status, PaymentStatus.PENDING)


def make_gateway(monobank_token: str, public_base_url: str) -> PaymentGateway | None:
    """No token -> online payment is switched off (owner decision, specs/006)."""
    if not monobank_token:
        return None
    return MonobankGateway(monobank_token, public_base_url)
