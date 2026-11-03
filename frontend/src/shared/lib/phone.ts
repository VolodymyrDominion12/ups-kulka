/** Same rule as backend `PhoneNumber.parse` (orders/domain/entities.py). */
export function normalizeUaPhone(raw: string): string | null {
  let digits = raw.replace(/\D/g, "");
  if (digits.length === 10 && digits.startsWith("0")) digits = `38${digits}`;
  if (digits.length !== 12 || !digits.startsWith("380")) return null;
  return `+${digits}`;
}
