"use client";

import React, { useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  ImagePlus,
  Loader2,
  Pencil,
  Search,
  Star,
  Trash2,
} from "lucide-react";
import {
  adminApi,
  formatMoneyUah,
  ProductOut,
  TagOut,
} from "@/shared/api/admin";
import {
  appendMediaIds,
  moveMediaToFront,
  removeMediaId,
  reorderMediaIds,
} from "@/shared/lib/gallery";

const TAG_GROUP_LABELS: Record<string, string> = {
  recipient: "Для кого",
  occasion: "Привід / Свято",
  type: "Тип композиції",
  color: "Колір / Стиль",
  theme: "Тематика",
  age: "Вік",
};

interface CatalogManageTabProps {
  products: ProductOut[];
  tags: TagOut[];
  onProductUpdated: (product: ProductOut) => void;
}

export function CatalogManageTab({
  products,
  tags,
  onProductUpdated,
}: CatalogManageTabProps) {
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editPriceUah, setEditPriceUah] = useState("");
  const [editOldPriceUah, setEditOldPriceUah] = useState("");
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editTagSlugs, setEditTagSlugs] = useState<string[]>([]);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [uploadingId, setUploadingId] = useState<string | null>(null);
  const [photoError, setPhotoError] = useState<string | null>(null);

  const filtered = products.filter((p) => {
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return (
      p.name.toLowerCase().includes(q) ||
      p.slug.toLowerCase().includes(q) ||
      (p.description && p.description.toLowerCase().includes(q)) ||
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
    setEditDescription(product.description || "");
    setEditPriceUah(String(Math.round(product.price_kopecks / 100)));
    setEditOldPriceUah(
      product.old_price_kopecks
        ? String(Math.round(product.old_price_kopecks / 100))
        : ""
    );
    setEditTagSlugs(product.tags.map((t) => t.slug));
  };

  const toggleEditTag = (slug: string) => {
    setEditTagSlugs((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug]
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
        description: editDescription.trim(),
        price_kopecks: newPrice * 100,
        old_price_kopecks:
          newOldPrice && newOldPrice > newPrice ? newOldPrice * 100 : null,
        clear_old_price: !newOldPrice,
        tag_slugs: editTagSlugs,
      });
      onProductUpdated(updated);
      setEditingId(null);
    } finally {
      setBusyId(null);
    }
  };

  const applyMedia = async (product: ProductOut, media_ids: string[]) => {
    setPhotoError(null);
    try {
      const updated = await adminApi.updateProduct(product.id, { media_ids });
      onProductUpdated(updated);
    } catch (err) {
      setPhotoError(
        err instanceof Error ? err.message : "Не вдалося зберегти фото"
      );
    }
  };

  const handleAddPhotos = async (product: ProductOut, files: FileList | null) => {
    if (!files || files.length === 0) return;
    const current = product.images.map((img) => img.media_id);
    const room = Math.max(0, 10 - current.length);
    const fileArray = Array.from(files).slice(0, room);
    if (fileArray.length === 0) return;

    setUploadingId(product.id);
    try {
      const added: string[] = [];
      for (const file of fileArray) {
        const asset = await adminApi.uploadMedia(file);
        added.push(asset.id);
      }
      await applyMedia(product, appendMediaIds(current, added, 10));
    } finally {
      setUploadingId(null);
    }
  };

  const mediaIds = (product: ProductOut) =>
    product.images.map((img) => img.media_id);

  const handleSetCover = (product: ProductOut, index: number) =>
    applyMedia(product, moveMediaToFront(mediaIds(product), index));

  const handleRemovePhoto = (product: ProductOut, index: number) =>
    applyMedia(product, removeMediaId(mediaIds(product), index));

  const handleMovePhoto = (product: ProductOut, index: number, delta: -1 | 1) =>
    applyMedia(product, reorderMediaIds(mediaIds(product), index, index + delta));

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
                      <Pencil className="h-3 w-3" /> Редагувати
                    </button>
                  </div>

                  {product.description && (
                    <p className="mt-1.5 line-clamp-2 text-xs text-neutral-600">
                      {product.description}
                    </p>
                  )}

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
                <div className="mt-3 space-y-2.5 border-t border-line pt-3">
                  <div>
                    <label className="mb-1 block text-[11px] font-semibold text-muted">
                      Назва товару чи послуги
                    </label>
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      placeholder="Назва товару чи послуги"
                      className="min-h-[40px] w-full rounded-xl border border-line bg-surface px-3 text-xs font-semibold text-ink focus:border-rose focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-[11px] font-semibold text-muted">
                      Опис товару чи послуги
                    </label>
                    <textarea
                      rows={3}
                      placeholder="Опис композиції, наповнення кульок або деталей послуги..."
                      value={editDescription}
                      onChange={(e) => setEditDescription(e.target.value)}
                      className="w-full rounded-xl border border-line bg-surface p-2.5 text-xs text-ink focus:border-rose focus:outline-none"
                    />
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="number"
                      placeholder="Ціна (грн)"
                      value={editPriceUah}
                      onChange={(e) => setEditPriceUah(e.target.value)}
                      className="min-h-[40px] rounded-xl border border-line bg-surface px-3 text-xs font-bold text-ink focus:border-rose focus:outline-none"
                    />
                    <input
                      type="number"
                      placeholder="Стара ціна"
                      value={editOldPriceUah}
                      onChange={(e) => setEditOldPriceUah(e.target.value)}
                      className="min-h-[40px] rounded-xl border border-line bg-surface px-3 text-xs text-ink focus:border-rose focus:outline-none"
                    />
                    <button
                      type="button"
                      onClick={() => saveEdit(product)}
                      className="inline-flex min-h-[40px] items-center justify-center gap-1 rounded-xl bg-ink text-xs font-bold text-white hover:bg-neutral-800 transition"
                    >
                      <Check className="h-3.5 w-3.5" /> Зберегти
                    </button>
                  </div>

                  {/* Multi-dimensional Tag Selector */}
                  {tags.length > 0 && (
                    <div className="space-y-2 rounded-2xl border border-line bg-surface/60 p-2.5">
                      <div className="text-[11px] font-bold text-muted">
                        Теги та кольори ({editTagSlugs.length})
                      </div>
                      {Object.keys(TAG_GROUP_LABELS).map((groupKey) => {
                        const groupItems = tags.filter((t) => t.group === groupKey);
                        if (groupItems.length === 0) return null;
                        return (
                          <div key={groupKey}>
                            <div className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-muted">
                              {TAG_GROUP_LABELS[groupKey]}
                            </div>
                            <div className="flex flex-wrap gap-1.5">
                              {groupItems.map((tag) => {
                                const active = editTagSlugs.includes(tag.slug);
                                return (
                                  <button
                                    key={tag.slug}
                                    type="button"
                                    onClick={() => toggleEditTag(tag.slug)}
                                    className={`min-h-[30px] rounded-full px-2.5 py-1 text-[11px] font-bold transition ${
                                      active
                                        ? "bg-rose-deep text-white shadow-sm"
                                        : "border border-line bg-white text-ink"
                                    }`}
                                  >
                                    {active ? "✓ " : ""}
                                    {tag.name}
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Photos */}
                  <div className="pt-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-muted">
                        Фото ({product.images.length}/10)
                      </span>
                      <label
                        className={`inline-flex min-h-[34px] cursor-pointer items-center gap-1 rounded-full px-3 text-[11px] font-bold text-rose-deep ${
                          uploadingId === product.id ? "opacity-50" : ""
                        }`}
                      >
                        {uploadingId === product.id ? (
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <ImagePlus className="h-3.5 w-3.5" />
                        )}
                        {uploadingId === product.id ? "Завантаження..." : "Додати фото"}
                        <input
                          type="file"
                          accept="image/jpeg,image/png,image/webp"
                          multiple
                          disabled={uploadingId === product.id}
                          className="hidden"
                          onChange={(e) => {
                            void handleAddPhotos(product, e.target.files);
                            e.target.value = "";
                          }}
                        />
                      </label>
                    </div>

                    {product.images.length > 0 ? (
                      <div className="mt-2 flex gap-2 overflow-x-auto pb-1">
                        {product.images.map((img, index) => (
                          <div
                            key={img.media_id}
                            className="relative h-24 w-20 shrink-0 overflow-hidden rounded-xl border border-line bg-surface"
                          >
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img
                              src={img.variants["320w"] || img.blur_data_url}
                              alt=""
                              className="h-full w-full object-cover"
                            />
                            {index === 0 && (
                              <span className="absolute left-1 top-1 rounded-full bg-ink/80 px-1.5 py-0.5 text-[9px] font-bold text-white">
                                Головне
                              </span>
                            )}
                            <div className="absolute inset-x-0 bottom-0 flex justify-center gap-0.5 bg-black/45 px-1 py-1">
                              {index > 0 && (
                                <button
                                  type="button"
                                  onClick={() => handleSetCover(product, index)}
                                  title="Зробити головним"
                                  className="flex h-6 w-6 items-center justify-center rounded-md bg-white/20 text-white"
                                >
                                  <Star className="h-3 w-3" />
                                </button>
                              )}
                              <button
                                type="button"
                                onClick={() => handleMovePhoto(product, index, -1)}
                                disabled={index === 0}
                                title="Ліворуч"
                                className="flex h-6 w-6 items-center justify-center rounded-md bg-white/20 text-white disabled:opacity-30"
                              >
                                <ArrowLeft className="h-3 w-3" />
                              </button>
                              <button
                                type="button"
                                onClick={() => handleMovePhoto(product, index, 1)}
                                disabled={index === product.images.length - 1}
                                title="Праворуч"
                                className="flex h-6 w-6 items-center justify-center rounded-md bg-white/20 text-white disabled:opacity-30"
                              >
                                <ArrowRight className="h-3 w-3" />
                              </button>
                              <button
                                type="button"
                                onClick={() => handleRemovePhoto(product, index)}
                                title="Видалити фото"
                                className="flex h-6 w-6 items-center justify-center rounded-md bg-white/20 text-rose-200"
                              >
                                <Trash2 className="h-3 w-3" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="mt-1.5 text-[11px] italic text-muted">
                        Немає фото — натисніть «Додати фото».
                      </p>
                    )}

                    {photoError && (
                      <p className="mt-1.5 text-[11px] font-semibold text-red-600">
                        {photoError}
                      </p>
                    )}
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
