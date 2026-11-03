import { formatUah } from "@/shared/lib/money";

interface Props {
  priceKopecks: number;
  oldPriceKopecks?: number | null;
  className?: string;
}

export function Price({ priceKopecks, oldPriceKopecks, className = "" }: Props) {
  const oldPrice = oldPriceKopecks && oldPriceKopecks > priceKopecks ? oldPriceKopecks : null;
  return (
    <p className={`font-extrabold tabular-nums text-rose-deep ${className}`}>
      {formatUah(priceKopecks)}
      {oldPrice !== null && (
        <s className="ml-2 text-[0.82em] font-medium text-muted">
          <span className="sr-only">Стара ціна </span>
          {formatUah(oldPrice)}
        </s>
      )}
    </p>
  );
}
