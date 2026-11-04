"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  Camera,
  Check,
  Copy,
  ImagePlus,
  Loader2,
  Plus,
  Sparkles,
  Trash2,
} from "lucide-react";
import {
  adminApi,
  formatMoneyUah,
  MediaAssetOut,
  ProductOut,
  TagOut,
} from "@/shared/api/admin";

const TAG_GROUP_LABELS: Record<string, string> = {
  recipient: "Для кого",
  occasion: "Привід / Свято",
  type: "Тип композиції",
  color: "Колір / Стиль",
  theme: "Тематика",
  age: "Вік",
};

const QUICK_PRICES_UAH = [650, 950, 1250, 1500, 1850, 2500];

interface QuickPublishTabProps {
  tags: TagOut[];
  onPublished: (product: ProductOut) => void;
  onTagsChanged: () => void;
  prefillPriceUah?: number | null;
  prefillName?: string | null;
}

export function QuickPublishTab({
  tags,
  onPublished,
  onTagsChanged,
  prefillPriceUah,
  prefillName,
}: QuickPublishTabProps) {
  const cameraInputRef = useRef<HTMLInputElement | null>(null);
  const galleryInputRef = useRef<HTMLInputElement | null>(null);

  const [uploadedAssets, setUploadedAssets] = useState<MediaAssetOut[]>([]);
  const [uploadingCount, setUploadingCount] = useState(0);
  const [name, setName] = useState(prefillName || "");
  const [priceUah, setPriceUah] = useState(
    prefillPriceUah ? String(prefillPriceUah) : ""
  );
  const [oldPriceUah, setOldPriceUah] = useState("");
  const [description, setDescription] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [publishedProduct, setPublishedProduct] = useState<ProductOut | null>(
    null
  );
  const [copied, setCopied] = useState(false);

  // Quick new tag modal state
  const [newTagGroup, setNewTagGroup] = useState<string | null>(null);
  const [newTagName, setNewTagName] = useState("");
  const [newTagSlug, setNewTagSlug] = useState("");

  useEffect(() => {
    if (prefillPriceUah) setPriceUah(String(prefillPriceUah));
    if (prefillName) setName(prefillName);
  }, [prefillPriceUah, prefillName]);

  const handleFilesSelected = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setError(null);
    const fileArray = Array.from(files).slice(0, 10);
    setUploadingCount((c) => c + fileArray.length);

    for (const file of fileArray) {
      try {
        const asset = await adminApi.uploadMedia(file);
        setUploadedAssets((prev) => [...prev, asset]);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Не вдалося завантажити фото"
        );
      } finally {
        setUploadingCount((c) => Math.max(0, c - 1));
      }
    }
  };

  const toggleTag = (slug: string) => {
    setSelectedTags((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug]
    );
  };

  const suggestNameFromTags = () => {
    const chosen = tags.filter((t) => selectedTags.includes(t.slug));
    if (chosen.length === 0) {
      setName("Святкова композиція з кульок");
      return;
    }
    const parts = chosen.slice(0, 3).map((t) => t.name);
    setName(`Композиція «${parts.join(" · ")}»`);
  };

  const handlePublish = async (isActive = true) => {
    setError(null);
    const numericPrice = Number(priceUah.replace(/[^\d]/g, ""));
    if (!numericPrice || numericPrice <= 0) {
      setError("Вкажіть ціну у гривнях");
      return;
    }
    const finalName = name.trim() || "Композиція з гелієвих кульок";
    const numericOldPrice = oldPriceUah
      ? Number(oldPriceUah.replace(/[^\d]/g, ""))
      : null;

    setSubmitting(true);
    try {
      const created = await adminApi.quickCreateProduct({
        name: finalName,
        price_kopecks: numericPrice * 100,
        old_price_kopecks:
          numericOldPrice && numericOldPrice > numericPrice
            ? numericOldPrice * 100
            : null,
        description: description.trim(),
        is_active: isActive,
        tag_slugs: selectedTags,
        media_ids: uploadedAssets.map((a) => a.id),
      });
      setPublishedProduct(created);
      onPublished(created);
      // Reset fields for the next salon composition
      setUploadedAssets([]);
      setName("");
      setPriceUah("");
      setOldPriceUah("");
      setDescription("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Помилка збереження товару"
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateQuickTag = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTagGroup || !newTagName.trim() || !newTagSlug.trim()) return;
    try {
      const created = await adminApi.createTag({
        group: newTagGroup,
        name: newTagName.trim(),
        slug: newTagSlug.trim().toLowerCase(),
      });
      onTagsChanged();
      setSelectedTags((prev) => [...prev, created.slug]);
      setNewTagGroup(null);
      setNewTagName("");
      setNewTagSlug("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Помилка створення тегу");
    }
  };

  const groupedTags = Object.keys(TAG_GROUP_LABELS).map((groupKey) => ({
    group: groupKey,
    label: TAG_GROUP_LABELS[groupKey],
    items: tags.filter((t) => t.group === groupKey),
  }));

  return (
    <div className="space-y-5 pb-28">
      {/* Success banner after express publish */}
      {publishedProduct && (
        <div className="rounded-3xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <div>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-600 px-2.5 py-0.5 text-xs font-semibold text-white">
                <Check className="h-3.5 w-3.5" /> На сайті!
              </span>
              <h3 className="mt-1.5 font-display text-base font-bold text-ink">
                {publishedProduct.name}
              </h3>
              <p className="text-xs text-muted">
                URL: /tovar/{publishedProduct.slug} ·{" "}
                {formatMoneyUah(publishedProduct.price_kopecks)}
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                navigator.clipboard.writeText(
                  `${window.location.origin}/tovar/${publishedProduct.slug}`
                );
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              }}
              className="inline-flex min-h-[42px] items-center gap-1.5 rounded-full bg-white px-3.5 py-2 text-xs font-semibold text-ink shadow-sm active:scale-95"
            >
              <Copy className="h-3.5 w-3.5" />
              {copied ? "Скопійовано" : "Посилання"}
            </button>
          </div>
        </div>
      )}

      {/* Step 1: Camera & Instant Background Upload */}
      <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-rose-deep">
              Крок 1 · Фото в салоні
            </span>
            <h2 className="font-display text-lg font-bold text-ink">
              Зніміть готову композицію
            </h2>
          </div>
          {uploadingCount > 0 && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-accent-soft px-3 py-1 text-xs font-semibold text-rose-deep">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Стискаємо у 4:5 WebP...
            </span>
          )}
        </div>

        <input
          ref={cameraInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          capture="environment"
          onChange={(e) => handleFilesSelected(e.target.files)}
          className="hidden"
        />
        <input
          ref={galleryInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          onChange={(e) => handleFilesSelected(e.target.files)}
          className="hidden"
        />

        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => cameraInputRef.current?.click()}
            className="flex min-h-[88px] flex-col items-center justify-center gap-1.5 rounded-2xl bg-rose-deep px-4 py-3 text-white shadow-pop transition active:scale-[0.98]"
          >
            <Camera className="h-7 w-7" />
            <span className="text-sm font-bold">📸 Зробити фото</span>
            <span className="text-[11px] opacity-80">Камера (авто 4:5)</span>
          </button>

          <button
            type="button"
            onClick={() => galleryInputRef.current?.click()}
            className="flex min-h-[88px] flex-col items-center justify-center gap-1.5 rounded-2xl border-2 border-dashed border-accent-dark bg-surface px-4 py-3 text-ink transition active:scale-[0.98]"
          >
            <ImagePlus className="h-7 w-7 text-rose-deep" />
            <span className="text-sm font-bold">З галереї</span>
            <span className="text-[11px] text-muted">До 10 фото</span>
          </button>
        </div>

        {uploadedAssets.length > 0 && (
          <div className="mt-4 flex gap-3 overflow-x-auto pb-1">
            {uploadedAssets.map((asset, index) => (
              <div
                key={asset.id}
                className="relative h-28 w-24 shrink-0 overflow-hidden rounded-2xl border border-line bg-surface"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={asset.variants["320w"] || asset.blur_data_url}
                  alt={asset.original_filename}
                  className="h-full w-full object-cover"
                />
                {index === 0 && (
                  <span className="absolute left-1.5 top-1.5 rounded-full bg-ink/80 px-2 py-0.5 text-[10px] font-bold text-white">
                    Головне
                  </span>
                )}
                <button
                  type="button"
                  onClick={() =>
                    setUploadedAssets((prev) =>
                      prev.filter((a) => a.id !== asset.id)
                    )
                  }
                  className="absolute bottom-1.5 right-1.5 flex h-7 w-7 items-center justify-center rounded-full bg-white/90 text-rose-deep shadow"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Step 2: Price & Name */}
      <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
        <span className="text-xs font-bold uppercase tracking-wider text-rose-deep">
          Крок 2 · Ціна та назва
        </span>

        <div className="mt-3 grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-muted">
              Ціна на сайті (грн) *
            </label>
            <input
              type="number"
              inputMode="numeric"
              placeholder="1450"
              value={priceUah}
              onChange={(e) => setPriceUah(e.target.value)}
              className="mt-1 min-h-[52px] w-full rounded-2xl border border-line bg-surface px-4 text-xl font-bold text-ink focus:border-rose focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-muted">
              Стара ціна (акція, грн)
            </label>
            <input
              type="number"
              inputMode="numeric"
              placeholder="1700"
              value={oldPriceUah}
              onChange={(e) => setOldPriceUah(e.target.value)}
              className="mt-1 min-h-[52px] w-full rounded-2xl border border-line bg-surface px-4 text-lg font-medium text-muted focus:border-rose focus:outline-none"
            />
          </div>
        </div>

        {/* Fast price chips for one-thumb entry */}
        <div className="mt-2.5 flex flex-wrap gap-1.5">
          {QUICK_PRICES_UAH.map((preset) => (
            <button
              key={preset}
              type="button"
              onClick={() => setPriceUah(String(preset))}
              className={`min-h-[36px] rounded-full px-3 text-xs font-bold transition ${
                priceUah === String(preset)
                  ? "bg-ink text-white"
                  : "bg-accent-soft/70 text-rose-deep hover:bg-accent-soft"
              }`}
            >
              {preset} ₴
            </button>
          ))}
        </div>

        <div className="mt-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-muted">
              Назва композиції (slug створиться сам)
            </label>
            <button
              type="button"
              onClick={suggestNameFromTags}
              className="inline-flex items-center gap-1 text-xs font-bold text-rose-deep"
            >
              <Sparkles className="h-3.5 w-3.5" /> Згенерувати з тегів
            </button>
          </div>
          <input
            type="text"
            placeholder="Напр.: Ніжний фонтан з цифрою 5"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 min-h-[48px] w-full rounded-2xl border border-line bg-surface px-4 text-base font-medium text-ink focus:border-rose focus:outline-none"
          />
        </div>

        <div className="mt-3">
          <label className="block text-xs font-semibold text-muted">
            Короткий склад / опис (опційно)
          </label>
          <textarea
            rows={2}
            placeholder="Фольгована цифра, 7 латексних кульок пастель, 3 конфеті, грузик..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="mt-1 w-full rounded-2xl border border-line bg-surface p-3 text-sm text-ink focus:border-rose focus:outline-none"
          />
        </div>
      </section>

      {/* Step 3: Tap Chips for Multi-dimensional Tags */}
      <section className="rounded-3xl border border-line bg-white p-4 shadow-sm">
        <div className="mb-2 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-rose-deep">
              Крок 3 · Куди додати на сайті
            </span>
            <h2 className="font-display text-base font-bold text-ink">
              Оберіть теги в 1 тап ({selectedTags.length})
            </h2>
          </div>
        </div>

        <div className="space-y-4">
          {groupedTags.map(({ group, label, items }) => (
            <div key={group}>
              <div className="mb-1.5 flex items-center justify-between">
                <span className="text-xs font-bold text-muted">{label}</span>
                <button
                  type="button"
                  onClick={() => setNewTagGroup(group)}
                  className="inline-flex items-center gap-0.5 text-xs font-semibold text-rose-deep"
                >
                  <Plus className="h-3.5 w-3.5" /> Додати тег
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {items.map((tag) => {
                  const active = selectedTags.includes(tag.slug);
                  return (
                    <button
                      key={tag.slug}
                      type="button"
                      onClick={() => toggleTag(tag.slug)}
                      className={`min-h-[42px] rounded-full px-3.5 py-2 text-xs font-bold transition active:scale-95 ${
                        active
                          ? "bg-rose-deep text-white shadow-sm"
                          : "border border-line bg-surface text-ink"
                      }`}
                    >
                      {active ? "✓ " : ""}
                      {tag.name}
                    </button>
                  );
                })}
                {items.length === 0 && (
                  <span className="text-xs italic text-muted">
                    Немає тегів у цій групі
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {newTagGroup && (
          <form
            onSubmit={handleCreateQuickTag}
            className="mt-4 rounded-2xl border border-accent bg-surface p-3"
          >
            <div className="text-xs font-bold text-rose-deep">
              Новий тег у «{TAG_GROUP_LABELS[newTagGroup]}»
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2">
              <input
                type="text"
                placeholder="Назва (укр)"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                className="min-h-[42px] rounded-xl border border-line bg-white px-3 text-xs"
              />
              <input
                type="text"
                placeholder="slug (lat, напр. vypyska)"
                value={newTagSlug}
                onChange={(e) => setNewTagSlug(e.target.value)}
                className="min-h-[42px] rounded-xl border border-line bg-white px-3 text-xs"
              />
            </div>
            <div className="mt-2 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setNewTagGroup(null)}
                className="rounded-full px-3 py-1.5 text-xs text-muted"
              >
                Скасувати
              </button>
              <button
                type="submit"
                className="rounded-full bg-ink px-4 py-1.5 text-xs font-bold text-white"
              >
                Створити
              </button>
            </div>
          </form>
        )}
      </section>

      {error && (
        <div className="rounded-2xl bg-red-50 px-4 py-3 text-xs font-semibold text-red-700">
          {error}
        </div>
      )}

      {/* Sticky Thumb Action Bar */}
      <div className="fixed bottom-16 left-0 right-0 z-30 mx-auto max-w-xl border-t border-line bg-white/95 px-4 py-2.5 backdrop-blur">
        <div className="flex gap-2.5">
          <button
            type="button"
            disabled={submitting || uploadingCount > 0}
            onClick={() => handlePublish(false)}
            className="min-h-[50px] rounded-full border border-line bg-surface px-4 text-xs font-bold text-ink disabled:opacity-50"
          >
            У чернетки
          </button>
          <button
            type="button"
            disabled={submitting || uploadingCount > 0}
            onClick={() => handlePublish(true)}
            className="flex min-h-[50px] flex-1 items-center justify-center gap-2 rounded-full bg-ink px-6 text-sm font-bold text-white shadow-pop transition active:scale-[0.99] disabled:opacity-50"
          >
            {submitting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "🎈 Опублікувати на сайт"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
