"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { ChevronLeft, Copy, Eye, EyeOff, ImagePlus, Loader2, Pencil, Plus, Trash2 } from "lucide-react";

import {
  adminApi,
  AdminBannerOut,
  BannerImageOut,
  BannerLayout,
  BannerPayload,
  BannerState,
  BannerTheme,
} from "@/shared/api/admin";
import { DEFAULT_HOME_BANNER, type HomeBannerOut } from "@/shared/api/storefront";
import { fromDateTimeLocal, toDateTimeLocal } from "@/shared/lib/banner";
import { Hero } from "@/widgets/hero";

const STATE_LABELS: Record<BannerState, { text: string; className: string }> = {
  active: { text: "Зараз на сайті", className: "bg-emerald-100 text-emerald-900" },
  scheduled: { text: "Заплановано", className: "bg-sky-100 text-sky-900" },
  expired: { text: "Завершено", className: "bg-neutral-200 text-neutral-700" },
  draft: { text: "Чернетка", className: "bg-amber-100 text-amber-900" },
};

const LAYOUT_LABELS: Record<BannerLayout, string> = {
  balloons: "Кульки (стандартний)",
  image: "Фонове фото",
  split: "Текст + фото (скоро)",
  collection: "Підбірка (скоро)",
};

const THEME_LABELS: Record<BannerTheme, string> = {
  rose: "Рожева",
  red: "Червона",
  gold: "Золота",
  dark: "Темна",
};

const SELECTABLE_LAYOUTS: BannerLayout[] = ["balloons", "image"];

interface PickedImage {
  id: string;
  image: BannerImageOut;
}

interface Draft {
  name: string;
  layout: BannerLayout;
  theme: BannerTheme;
  headline: string;
  subtitle: string;
  ctaLabel: string;
  ctaUrl: string;
  cta2Label: string;
  cta2Url: string;
  priority: string;
  startsAt: string;
  endsAt: string;
  imageAlt: string;
  photo: PickedImage | null;
  photoMobile: PickedImage | null;
}

function newDraft(): Draft {
  const start = new Date();
  start.setMinutes(0, 0, 0);
  const end = new Date(start.getTime() + 7 * 24 * 60 * 60 * 1000);
  return {
    name: "",
    layout: "balloons",
    theme: "rose",
    headline: "",
    subtitle: "",
    ctaLabel: "",
    ctaUrl: "",
    cta2Label: "",
    cta2Url: "",
    priority: "0",
    startsAt: toDateTimeLocal(start.toISOString()),
    endsAt: toDateTimeLocal(end.toISOString()),
    imageAlt: "",
    photo: null,
    photoMobile: null,
  };
}

function draftFromBanner(banner: AdminBannerOut): Draft {
  return {
    name: banner.name,
    layout: banner.layout,
    theme: banner.theme,
    headline: banner.headline,
    subtitle: banner.subtitle,
    ctaLabel: banner.cta_label,
    ctaUrl: banner.cta_url,
    cta2Label: banner.cta2_label,
    cta2Url: banner.cta2_url,
    priority: String(banner.priority),
    startsAt: toDateTimeLocal(banner.starts_at),
    endsAt: toDateTimeLocal(banner.ends_at),
    imageAlt: banner.image_alt,
    photo: banner.media_id && banner.image ? { id: banner.media_id, image: banner.image } : null,
    photoMobile:
      banner.media_mobile_id && banner.image_mobile
        ? { id: banner.media_mobile_id, image: banner.image_mobile }
        : null,
  };
}

function toPayload(draft: Draft): BannerPayload {
  return {
    name: draft.name.trim(),
    layout: draft.layout,
    starts_at: fromDateTimeLocal(draft.startsAt),
    ends_at: fromDateTimeLocal(draft.endsAt),
    headline: draft.headline.trim(),
    subtitle: draft.subtitle.trim(),
    priority: Number.parseInt(draft.priority, 10) || 0,
    cta_label: draft.ctaLabel.trim(),
    cta_url: draft.ctaUrl.trim(),
    cta2_label: draft.cta2Label.trim(),
    cta2_url: draft.cta2Url.trim(),
    media_id: draft.photo?.id ?? null,
    media_mobile_id: draft.photoMobile?.id ?? null,
    image_alt: draft.imageAlt.trim(),
    theme: draft.theme,
  };
}

function previewBanner(draft: Draft): HomeBannerOut {
  return {
    ...DEFAULT_HOME_BANNER,
    layout: draft.layout,
    campaign_id: "preview",
    theme: draft.theme,
    headline: draft.headline,
    subtitle: draft.subtitle,
    cta_label: draft.ctaLabel,
    cta_url: draft.ctaUrl || "/kulky",
    cta2_label: draft.cta2Label,
    cta2_url: draft.cta2Url || "/kulky",
    image: draft.photo?.image ?? null,
    image_mobile: draft.photoMobile?.image ?? null,
    image_alt: draft.imageAlt,
  };
}

function formatPeriod(startsAt: string, endsAt: string): string {
  const format = (iso: string) =>
    new Date(iso).toLocaleString("uk-UA", {
      timeZone: "Europe/Kyiv",
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  return `${format(startsAt)} — ${format(endsAt)}`;
}

const INPUT =
  "mt-1 min-h-[44px] w-full rounded-xl border border-line bg-surface px-3 text-sm text-ink focus:border-rose focus:outline-none";

function Field({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
  hint,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  placeholder?: string;
  hint?: string;
}) {
  return (
    <label className="block">
      <span className="text-xs font-semibold text-muted">{label}</span>
      <input
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className={INPUT}
      />
      {hint && <span className="mt-0.5 block text-[11px] text-muted">{hint}</span>}
    </label>
  );
}

function PhotoPicker({
  label,
  hint,
  photo,
  onChange,
  onError,
}: {
  label: string;
  hint: string;
  photo: PickedImage | null;
  onChange: (photo: PickedImage | null) => void;
  onError: (message: string) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const upload = async (file: File | undefined) => {
    if (!file) return;
    setUploading(true);
    try {
      const asset = await adminApi.uploadMedia(file);
      onChange({ id: asset.id, image: asset });
    } catch (err) {
      onError(err instanceof Error ? err.message : "Не вдалося завантажити фото");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  const thumb = photo ? (photo.image.variants["320w"] ?? photo.image.variants.original) : null;

  return (
    <div>
      <span className="text-xs font-semibold text-muted">{label}</span>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={(e) => void upload(e.target.files?.[0])}
        className="hidden"
      />
      <div className="mt-1 flex items-center gap-3">
        {thumb ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={thumb} alt="" className="h-16 w-24 rounded-lg border border-line object-cover" />
        ) : (
          <div className="flex h-16 w-24 items-center justify-center rounded-lg border border-dashed border-line text-muted">
            <ImagePlus className="h-5 w-5" />
          </div>
        )}
        <div className="flex flex-col gap-1.5">
          <button
            type="button"
            disabled={uploading}
            onClick={() => inputRef.current?.click()}
            className="inline-flex min-h-[36px] items-center gap-1.5 rounded-full bg-surface px-3 text-xs font-bold text-rose-deep"
          >
            {uploading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : null}
            {photo ? "Замінити" : "Завантажити"}
          </button>
          {photo && (
            <button
              type="button"
              onClick={() => onChange(null)}
              className="text-left text-[11px] font-semibold text-muted underline"
            >
              Прибрати
            </button>
          )}
        </div>
      </div>
      <span className="mt-0.5 block text-[11px] text-muted">{hint}</span>
    </div>
  );
}

function BannerForm({
  banner,
  onBack,
  onSaved,
}: {
  banner: AdminBannerOut | null;
  onBack: () => void;
  onSaved: () => void;
}) {
  const [draft, setDraft] = useState<Draft>(() => (banner ? draftFromBanner(banner) : newDraft()));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = <K extends keyof Draft>(key: K, value: Draft[K]) =>
    setDraft((prev) => ({ ...prev, [key]: value }));

  const layouts = SELECTABLE_LAYOUTS.includes(draft.layout)
    ? SELECTABLE_LAYOUTS
    : [...SELECTABLE_LAYOUTS, draft.layout];

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = toPayload(draft);
      if (banner) await adminApi.updateBanner(banner.id, payload);
      else await adminApi.createBanner(payload);
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не вдалося зберегти");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={save} className="space-y-4 pb-24">
      <button
        type="button"
        onClick={onBack}
        className="inline-flex items-center gap-1 text-xs font-bold text-muted"
      >
        <ChevronLeft className="h-4 w-4" /> До списку
      </button>

      <section className="space-y-1.5">
        <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Так це побачать клієнти</h3>
        <div className="overflow-hidden rounded-2xl border border-line">
          <Hero banner={previewBanner(draft)} showcase={[]} />
        </div>
        {draft.layout === "image" && !draft.photo && (
          <p className="text-[11px] font-semibold text-amber-700">
            Додайте фото, інакше на сайті буде стандартний банер.
          </p>
        )}
      </section>

      <div className="space-y-3 rounded-2xl border border-line bg-white p-3.5">
        <Field
          label="Назва кампанії (лише для вас)"
          value={draft.name}
          onChange={(v) => set("name", v)}
          placeholder="8 Березня 2027"
        />
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="text-xs font-semibold text-muted">Макет</span>
            <select
              value={draft.layout}
              onChange={(e) => set("layout", e.target.value as BannerLayout)}
              className={INPUT}
            >
              {layouts.map((layout) => (
                <option key={layout} value={layout} disabled={!SELECTABLE_LAYOUTS.includes(layout)}>
                  {LAYOUT_LABELS[layout]}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-xs font-semibold text-muted">Колір</span>
            <select
              value={draft.theme}
              onChange={(e) => set("theme", e.target.value as BannerTheme)}
              className={INPUT}
            >
              {(Object.keys(THEME_LABELS) as BannerTheme[]).map((theme) => (
                <option key={theme} value={theme}>
                  {THEME_LABELS[theme]}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="space-y-3 rounded-2xl border border-line bg-white p-3.5">
        <Field
          label="Заголовок"
          value={draft.headline}
          onChange={(v) => set("headline", v)}
          placeholder="З 8 Березня!"
        />
        <Field
          label="Підзаголовок"
          value={draft.subtitle}
          onChange={(v) => set("subtitle", v)}
          placeholder="Букети з кульок із доставкою по Києву"
        />
        <div className="grid grid-cols-2 gap-3">
          <Field label="Кнопка 1: текст" value={draft.ctaLabel} onChange={(v) => set("ctaLabel", v)} />
          <Field
            label="Кнопка 1: посилання"
            value={draft.ctaUrl}
            onChange={(v) => set("ctaUrl", v)}
            placeholder="/kulky"
          />
          <Field label="Кнопка 2: текст" value={draft.cta2Label} onChange={(v) => set("cta2Label", v)} />
          <Field
            label="Кнопка 2: посилання"
            value={draft.cta2Url}
            onChange={(v) => set("cta2Url", v)}
            placeholder="https://…"
          />
        </div>
        <p className="text-[11px] text-muted">
          Посилання: /сторінка на сайті або https://… Текст і посилання кнопки заповнюються разом.
        </p>
      </div>

      {draft.layout === "image" && (
        <div className="space-y-3 rounded-2xl border border-line bg-white p-3.5">
          <PhotoPicker
            label="Фото (комп’ютер)"
            hint="Широке, від 1600 px. Текст ляже зліва, тож важливе тримайте праворуч."
            photo={draft.photo}
            onChange={(photo) => set("photo", photo)}
            onError={setError}
          />
          <PhotoPicker
            label="Фото для телефона (необов’язково)"
            hint="Якщо не додати, телефон покаже фото для комп’ютера."
            photo={draft.photoMobile}
            onChange={(photo) => set("photoMobile", photo)}
            onError={setError}
          />
          <Field
            label="Опис фото (для незрячих і Google)"
            value={draft.imageAlt}
            onChange={(v) => set("imageAlt", v)}
            placeholder="Букет червоних кульок-сердець"
          />
        </div>
      )}

      <div className="space-y-3 rounded-2xl border border-line bg-white p-3.5">
        <div className="grid grid-cols-2 gap-3">
          <Field
            label="Показувати з"
            type="datetime-local"
            value={draft.startsAt}
            onChange={(v) => set("startsAt", v)}
          />
          <Field
            label="Показувати до"
            type="datetime-local"
            value={draft.endsAt}
            onChange={(v) => set("endsAt", v)}
          />
        </div>
        <Field
          label="Пріоритет"
          type="number"
          value={draft.priority}
          onChange={(v) => set("priority", v)}
          hint="Якщо періоди перетинаються, показується кампанія з більшим числом."
        />
        <p className="text-[11px] text-muted">
          Час за вашим годинником. Кампанія з’явиться на сайті, коли ви її опублікуєте й настане дата початку.
        </p>
      </div>

      {error && <p className="rounded-xl bg-red-50 px-3 py-2 text-xs font-semibold text-red-700">{error}</p>}

      <button
        type="submit"
        disabled={saving}
        className="flex min-h-[50px] w-full items-center justify-center rounded-full bg-ink text-sm font-bold text-white shadow-pop"
      >
        {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : banner ? "Зберегти" : "Створити чернетку"}
      </button>
    </form>
  );
}

export function BannersTab() {
  const [banners, setBanners] = useState<AdminBannerOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [editing, setEditing] = useState<AdminBannerOut | "new" | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      setBanners((await adminApi.listBanners()).items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не вдалося завантажити банери");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const run = async (id: string, action: () => Promise<unknown>) => {
    setBusyId(id);
    setError(null);
    try {
      await action();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Дію не виконано");
    } finally {
      setBusyId(null);
    }
  };

  const remove = (banner: AdminBannerOut) => {
    if (!window.confirm(`Видалити «${banner.name}»? Це не можна скасувати.`)) return;
    void run(banner.id, () => adminApi.deleteBanner(banner.id));
  };

  if (editing) {
    return (
      <BannerForm
        banner={editing === "new" ? null : editing}
        onBack={() => setEditing(null)}
        onSaved={() => {
          setEditing(null);
          void load();
        }}
      />
    );
  }

  return (
    <div className="space-y-3 pb-24">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted">Банер головної за святами: створіть наперед, він увімкнеться сам.</p>
        <button
          type="button"
          onClick={() => setEditing("new")}
          className="inline-flex min-h-[40px] shrink-0 items-center gap-1 rounded-full bg-rose-deep px-4 text-xs font-bold text-white"
        >
          <Plus className="h-4 w-4" /> Новий
        </button>
      </div>

      {error && <p className="rounded-xl bg-red-50 px-3 py-2 text-xs font-semibold text-red-700">{error}</p>}

      {loading ? (
        <Loader2 className="mx-auto mt-8 h-6 w-6 animate-spin text-rose-deep" />
      ) : banners.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-line p-6 text-center text-sm text-muted">
          Кампаній ще немає. На сайті показується стандартний банер з кульками.
        </p>
      ) : (
        banners.map((banner) => {
          const state = STATE_LABELS[banner.state];
          const busy = busyId === banner.id;
          return (
            <article key={banner.id} className="rounded-2xl border border-line bg-white p-3.5">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h3 className="truncate text-sm font-extrabold text-ink">{banner.name}</h3>
                  <p className="mt-0.5 text-[11px] text-muted">{formatPeriod(banner.starts_at, banner.ends_at)}</p>
                  <p className="mt-0.5 text-[11px] text-muted">
                    {LAYOUT_LABELS[banner.layout]} · пріоритет {banner.priority}
                  </p>
                </div>
                <span className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-bold ${state.className}`}>
                  {state.text}
                </span>
              </div>

              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => setEditing(banner)}
                  className="inline-flex min-h-[36px] items-center gap-1 rounded-full bg-surface px-3 text-xs font-bold text-ink"
                >
                  <Pencil className="h-3.5 w-3.5" /> Редагувати
                </button>
                {banner.status === "draft" ? (
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => void run(banner.id, () => adminApi.publishBanner(banner.id))}
                    className="inline-flex min-h-[36px] items-center gap-1 rounded-full bg-emerald-600 px-3 text-xs font-bold text-white"
                  >
                    <Eye className="h-3.5 w-3.5" /> Опублікувати
                  </button>
                ) : (
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => void run(banner.id, () => adminApi.unpublishBanner(banner.id))}
                    className="inline-flex min-h-[36px] items-center gap-1 rounded-full bg-surface px-3 text-xs font-bold text-ink"
                  >
                    <EyeOff className="h-3.5 w-3.5" /> Зняти
                  </button>
                )}
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => void run(banner.id, () => adminApi.duplicateBanner(banner.id))}
                  className="inline-flex min-h-[36px] items-center gap-1 rounded-full bg-surface px-3 text-xs font-bold text-ink"
                  title="Копія на наступний рік (чернетка)"
                >
                  <Copy className="h-3.5 w-3.5" /> На наступний рік
                </button>
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => remove(banner)}
                  className="inline-flex min-h-[36px] items-center gap-1 rounded-full px-3 text-xs font-bold text-rose-deep"
                >
                  <Trash2 className="h-3.5 w-3.5" /> Видалити
                </button>
              </div>
            </article>
          );
        })
      )}
    </div>
  );
}

