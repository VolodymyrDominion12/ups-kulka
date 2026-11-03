import uuid

import pytest

from tests.fakes.orders import (
    FakePaymentGateway,
    FakePaymentsUnitOfWork,
    RecordingPaymentNotifier,
)
from ups_kulka.modules.payments.application.dto import StartPaymentCommand
from ups_kulka.modules.payments.application.use_cases.confirm_payment import ConfirmPayment
from ups_kulka.modules.payments.application.use_cases.start_payment import StartPayment
from ups_kulka.modules.payments.domain.entities import Payment, PaymentStatus
from ups_kulka.modules.payments.domain.errors import (
    InvalidPayment,
    OnlinePaymentUnavailable,
    PaymentNotFound,
    PaymentsDisabled,
)
from ups_kulka.shared.domain.money import Money

CMD = StartPaymentCommand(
    order_id=uuid.uuid4(), order_number=1001, amount_kopecks=95000, description="№1001"
)


def _payment() -> Payment:
    return Payment.create(order_id=uuid.uuid4(), order_number=1, amount=Money(100), provider="x")


@pytest.mark.parametrize(
    ("steps", "final", "changes"),
    [
        ([PaymentStatus.PAID], PaymentStatus.PAID, [True]),
        ([PaymentStatus.PAID, PaymentStatus.PAID], PaymentStatus.PAID, [True, False]),
        ([PaymentStatus.PAID, PaymentStatus.PENDING], PaymentStatus.PAID, [True, False]),
        ([PaymentStatus.FAILED, PaymentStatus.PAID], PaymentStatus.PAID, [True, True]),
        ([PaymentStatus.PAID, PaymentStatus.REFUNDED], PaymentStatus.REFUNDED, [True, True]),
    ],
)
def test_status_transitions_are_idempotent(
    steps: list[PaymentStatus], final: PaymentStatus, changes: list[bool]
) -> None:
    payment = _payment()
    assert [payment.apply(step) for step in steps] == changes
    assert payment.status is final


def test_zero_amount_is_rejected() -> None:
    with pytest.raises(InvalidPayment):
        Payment.create(order_id=uuid.uuid4(), order_number=1, amount=Money(0), provider="x")


async def test_start_payment_stores_invoice() -> None:
    uow = FakePaymentsUnitOfWork()
    link = await StartPayment(uow, FakePaymentGateway())(CMD)
    assert link.page_url == "https://pay.example/x"
    assert uow.payments.by_invoice["inv-1001"].amount == Money(95000)
    assert uow.commits == 1


async def test_start_payment_without_gateway() -> None:
    use_case = StartPayment(FakePaymentsUnitOfWork(), None)
    assert not use_case.is_enabled
    with pytest.raises(OnlinePaymentUnavailable):
        await use_case(CMD)


async def test_webhook_marks_paid_and_notifies_once() -> None:
    uow, gateway, notifier = (
        FakePaymentsUnitOfWork(),
        FakePaymentGateway(),
        RecordingPaymentNotifier(),
    )
    await StartPayment(uow, gateway)(CMD)
    confirm = ConfirmPayment(uow, gateway, notifier)

    await confirm("inv-1001")
    await confirm("inv-1001")  # the bank repeats webhooks

    assert uow.payments.by_invoice["inv-1001"].status is PaymentStatus.PAID
    assert notifier.sent == [1001]
    assert uow.payments.saves == 1


async def test_webhook_for_unknown_invoice_does_not_call_the_bank() -> None:
    gateway = FakePaymentGateway()
    with pytest.raises(PaymentNotFound):
        await ConfirmPayment(FakePaymentsUnitOfWork(), gateway, RecordingPaymentNotifier())("nope")
    assert gateway.status_calls == 0


async def test_webhook_when_payments_are_off() -> None:
    with pytest.raises(PaymentsDisabled):
        await ConfirmPayment(FakePaymentsUnitOfWork(), None, RecordingPaymentNotifier())("x")


async def test_notification_failure_does_not_fail_the_webhook() -> None:
    uow, gateway = FakePaymentsUnitOfWork(), FakePaymentGateway()
    await StartPayment(uow, gateway)(CMD)
    await ConfirmPayment(uow, gateway, RecordingPaymentNotifier(fail=True))("inv-1001")
    assert uow.payments.by_invoice["inv-1001"].is_paid
