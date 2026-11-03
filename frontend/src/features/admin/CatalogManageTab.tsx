"use client";

import React, { useState } from "react";
import { Check, Eye, EyeOff, Loader2, Pencil, Search } from "lucide-react";
import { adminApi, formatMoneyUah, ProductOut } from "@/shared/api/admin";

interface CatalogManageTabProps {
  products: ProductOut[];
  onProductUpdated: (product: ProductOut) => void;
}

export function CatalogManageTab({
  products,
  onProductUpdated,
}: CatalogManageTabProps) {
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editPriceUah, setEditPriceUah] = useState("");
  const [editOldPriceUah, setEditOldPriceUah] = useState("");
  const [editName, setEditName] = useState("");
  const [busyId, setBusyId] = useState<string | null>(null);

  const filtered = products.filter((p) => {
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return (
      p.name.toLowerCase().includes(q) ||
      p.slug.toLowerCase().includes(q) ||
      p.tags.some((t) => t.name.toLowerCase().includes(q))
    );
  });

  const handleToggleActive = async (product: ProductOut) => {
    setBusyId(product.id);
    try {
      const updated = await adminApi.updateProduct(product.id, {
        is_active: !product.is_active,
      });
      onProductUpdated(updated);
    } finally {
      setBusyId(null);
    }
  };

  const startEditing = (product: ProductOut) => {
    setEditingId(product.id);
    setEditName(product.name);
    setEditPriceUah(String(Math.round(product.price_kopecks / 100)));
    setEditOldPriceUah(
      product.old_price_kopecks
        ? String(Math.round(product.old_price_kopecks / 100))
        : ""
    );
  };

  const saveEdit = async (product: ProductOut) => {
    const newPrice = Number(editPriceUah.replace(/[^\d]/g, ""));
    if (!newPrice || newPrice <= 0) return;
    const newOldPrice = editOldPriceUah
      ? Number(editOldPriceUah.replace(/[^\d]/g, ""))
      : null;

    setBusyId(product.id);
    try {
      const updated = await adminApi.updateProduct(product.id, {
        name: editName.trim() || product.name,
        price_kopecks: newPrice * 100,
        old_price_kopecks:
          newOldPrice && newOldPrice > newPrice ? newOldPrice * 100 : null,
        clear_old_price: !newOldPrice,
      });
      onProductUpdated(updated);
      setEditingId(null);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="space-y-4 pb-24">
      <div className="relative">
        <Search className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-muted" />
        <input
          type="search"
          placeholder="Пошук за назвою або тегом..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="min-h-[44px] w-full rounded-full border border-line bg-white pl-10 pr-4 text-sm text-ink focus:border-rose focus:outline-none"
        />
      </div>

      <div className="space-y-2.5">
        {filtered.map((product) => {
          const cover = product.images[0];
          const isEditing = editingId === product.id;

          return (
            <div
              key={product.id}
              className={`rounded-3xl border bg-white p-3.5 shadow-sm transition ${
                product.is_active
                  ? "border-line"
                  : "border-dashed border-neutral-300 opacity-70"
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="h-20 w-16 shrink-0 overflow-hidden rounded-2xl bg-surface">
                  {cover ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={cover.variants["320w"] || cover.blur_data_url}
                      alt={product.name}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-xl">
                      🎈
                    </div>
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="truncate font-display text-sm font-bold text-ink">
                      {product.name}
                    </h3>
                    <button
                      type="button"
                      disabled={busyId === product.id}
                      onClick={() => handleToggleActive(product)}
                      className={`inline-flex min-h-[32px] shrink-0 items-center gap-1 rounded-full px-2.5 text-[11px] font-bold ${
                        product.is_active
                          ? "bg-emerald-100 text-emerald-900"
                          : "bg-neutral-200 text-neutral-700"
                      }`}
                    >
                      {busyId === product.id ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : product.is_active ? (
                        <>
                          <Eye className="h-3 w-3" /> На сайті
                        </>
                      ) : (
                        <>
                          <EyeOff className="h-3 w-3" /> Приховано
                        </>
                      )}
                    </button>
                  </div>

                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="font-display text-base font-extrabold text-ink">
                      {formatMoneyUah(product.price_kopecks)}
                    </span>
                    {product.old_price_kopecks && (
                      <span className="text-xs text-muted line-through">
                        {formatMoneyUah(product.old_price_kopecks)}
                      </span>
                    )}
                    <button
                      type="button"
                      onClick={() => startEditing(product)}
                      className="ml-auto inline-flex items-center gap-1 rounded-full bg-surface px-2.5 py-1 text-[11px] font-semibold text-ink"
                    >
                      <Pencil className="h-3 w-3" /> Ціна / Назва
                    </button>
                  </div>

                  {product.tags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {product.tags.slice(0, 5).map((tag) => (
                        <span
                          key={tag.slug}
                          className="rounded-full bg-accent-soft/60 px-2 py-0.5 text-[10px] font-semibold text-rose-deep"
                        >
                          {tag.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {isEditing && (
                <div className="mt-3 space-y-2 border-t border-line pt-3">
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="min-h-[40px] w-full rounded-xl border border-line bg-surface px-3 text-xs font-semibold"
                  />
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="number"
                      placeholder="Ціна (грн)"
                      value={editPriceUah}
                      onChange={(e) => setEditPriceUah(e.target.value)}
                      className="min-h-[40px] rounded-xl border border-line bg-surface px-3 text-xs font-bold"
                    />
                    <input
                      type="number"
                      placeholder="Стара ціна"
                      value={editOldPriceUah}
                      onChange={(e) => setEditOldPriceUah(e.target.value)}
                      className="min-h-[40px] rounded-xl border border-line bg-surface px-3 text-xs"
                    />
                    <button
                      type="button"
                      onClick={() => saveEdit(product)}
                      className="inline-flex min-h-[40px] items-center justify-center gap-1 rounded-xl bg-ink text-xs font-bold text-white"
                    >
                      <Check className="h-3.5 w-3.5" /> Зберегти
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
