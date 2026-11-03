import { describe, expect, it } from "vitest";

import { cartReducer, type CartState } from "../cart";
import {
  buildOrderBody,
  kyivToday,
  orderErrorMessage,
  validateCheckout,
  type CheckoutForm,
} from "../checkout";

const cart: CartState = cartReducer(
  {},
  { type: "add", product: { id: "p1", slug: "sertse", name: "Серце", priceKopecks: 15500, imageUrl: null } },
);

const form: CheckoutForm = {
  name: " Олена ",
  phone: "093 111 22 33",
  deliveryMethod: "pickup",
  address: "вул. Хрещатик, 1",
  date: "",
  timeSlot: "",
  comment: "  Напис «Соня» ",
  paymentMethod: "on_delivery",
};

describe("validateCheckout", () => {
  it("accepts a valid pickup order", () => {
    expect(validateCheckout(form, cart, "2026-11-03")).toEqual({});
  });

  it("requires name, valid phone and a non-empty cart", () => {
    const errors = validateCheckout({ ...form, name: " ", phone: "12345" }, {}, "2026-11-03");
    expect(Object.keys(errors).sort()).toEqual(["cart", "name", "phone"]);
  });

  it("requires an address only for taxi", () => {
    const noAddress = { ...form, address: "  " };
    expect(validateCheckout(noAddress, cart, "2026-11-03").address).toBeUndefined();
    expect(validateCheckout({ ...noAddress, deliveryMethod: "taxi" }, cart, "2026-11-03").address).toBeTruthy();
  });

  it("rejects past dates, accepts today", () => {
    expect(validateCheckout({ ...form, date: "2026-11-02" }, cart, "2026-11-03").date).toBeTruthy();
    expect(validateCheckout({ ...form, date: "2026-11-03" }, cart, "2026-11-03").date).toBeUndefined();
  });
});

describe("buildOrderBody", () => {
  it("matches PlaceOrderIn: trimmed, normalized phone, no address for pickup", () => {
    const body = buildOrderBody(form, cart, null);
    expect(body).toEqual({
      customer: { name: "Олена", phone: "+380931112233", comment: "Напис «Соня»" },
      delivery: { method: "pickup", address: null, date: null, time_slot: null },
      payment_method: "on_delivery",
      items: [{ product_id: "p1", quantity: 1 }],
      marketing: null,
    });
  });

  it("keeps address, date and slot for taxi and passes attribution", () => {
    const marketing = {
      utm_source: "instagram",
      utm_medium: null,
      utm_campaign: null,
      promo_code: null,
      landing_page: "/",
    };
    const body = buildOrderBody(
      { ...form, deliveryMethod: "taxi", date: "2026-11-05", timeSlot: "14–16" },
      cart,
      marketing,
    );
    expect(body.delivery).toEqual({
      method: "taxi",
      address: "вул. Хрещатик, 1",
      date: "2026-11-05",
      time_slot: "14–16",
    });
    expect(body.marketing).toBe(marketing);
  });
});

describe("orderErrorMessage", () => {
  it("uses the server message", () => {
    expect(orderErrorMessage(422, { code: "address_required", message: "Для доставки таксі вкажіть адресу" }))
      .toBe("Для доставки таксі вкажіть адресу");
  });

  it("points to the cart when products are gone", () => {
    expect(orderErrorMessage(422, { code: "product_unavailable", message: "x" })).toContain("кошик");
  });

  it("explains validation and server errors without a message", () => {
    expect(orderErrorMessage(422, { detail: [] })).toContain("поля");
    expect(orderErrorMessage(502, null)).toContain("Спробуйте ще раз");
  });
});

describe("kyivToday", () => {
  it("uses the Kyiv date, not UTC", () => {
    // 23:30 UTC on 3 Nov is already 4 Nov in Kyiv (UTC+2).
    expect(kyivToday(new Date("2026-11-03T23:30:00Z"))).toBe("2026-11-04");
  });
});
