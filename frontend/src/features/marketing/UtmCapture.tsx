"use client";

import { useEffect } from "react";

import { attributionFromUrl } from "@/shared/lib/utm";

export const ATTRIBUTION_STORAGE_KEY = "ups_kulka_attribution_v1";

/** Remembers the first visit's ad marks for this browser tab session. */
export function UtmCapture() {
  useEffect(() => {
    try {
      if (window.sessionStorage.getItem(ATTRIBUTION_STORAGE_KEY)) return;
      const attribution = attributionFromUrl(new URL(window.location.href));
      if (attribution) {
        window.sessionStorage.setItem(ATTRIBUTION_STORAGE_KEY, JSON.stringify(attribution));
      }
    } catch {
      // Storage blocked: the order is placed without attribution.
    }
  }, []);
  return null;
}
