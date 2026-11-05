import Link from "next/link";

import { isExternalLink } from "@/shared/lib/banner";

const BASE = "inline-flex h-12 items-center rounded-full px-6 font-bold transition";

export function HeroButton({
  href,
  className,
  children,
}: {
  href: string;
  className: string;
  children: React.ReactNode;
}) {
  const classes = `${BASE} ${className}`;
  if (isExternalLink(href)) {
    return (
      <a href={href} target="_blank" rel="noreferrer" className={classes}>
        {children}
      </a>
    );
  }
  return (
    <Link href={href} className={classes}>
      {children}
    </Link>
  );
}
