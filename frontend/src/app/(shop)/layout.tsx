import type { ReactNode } from "react";

import { ShopShell } from "@/widgets/ShopShell";

export default function ShopLayout({ children }: { children: ReactNode }) {
  return <ShopShell>{children}</ShopShell>;
}
