"use client";

import React, { useCallback, useEffect, useState } from "react";
import { ChevronLeft, Loader2, Plus, Save, Search, Trash2 } from "lucide-react";
import { adminApi, TagDetailOut, TagSummaryOut } from "@/shared/api/admin";

const GROUP_LABELS: Record<string, string> = {
  recipient: "Для кого",
  occasion: "Привід",
  type: "Тип",
  color: "Колір",
  theme: "Тема",
  age: "Вік",
};

interface FaqDraft {
  question: string;
  answer: string;
}

export function TagSeoTab() {
  const [tags, setTags] = useState<TagSummaryOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [groupFilter, setGroupFilter] = useState<string>("all");

  // New tag creation modal state
  const [creatingTag, setCreatingTag] = useState(false);
  const [newGroup, setNewGroup] = useState<string>("color");
  const [newName, setNewName] = useState("");
  const [newSlug, setNewSlug] = useState("");

  const [selected, setSelected] = useState<TagDetailOut | null>(null);
  const [seoTitle, setSeoTitle] = useState("");
  const [seoDescription, setSeoDescription] = useState("");
  const [introText, setIntroText] = useState("");
  const [seoText, setSeoText] = useState("");
  const [faq, setFaq] = useState<FaqDraft[]>([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setTags(await adminApi.listTags());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не вдалося завантажити теги");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleCreateTag = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newSlug.trim()) return;
    setError(null);
    try {
      const created = await adminApi.createTag({
        group: newGroup,
        name: newName.trim(),
        slug: newSlug.trim().toLowerCase(),
      });
      setCreatingTag(false);
      setNewName("");
      setNewSlug("");
      await load();
      await openTag(created.slug);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не вдалося створити тег");
    }
  };

  const openTag = async (slug: string) => {
    setError(null);
    setSaved(false);
    try {
      const detail = await adminApi.getTagSeo(slug);
      setSelected(detail);
      setSeoTitle(detail.seo_title);
      setSeoDescription(detail.seo_description);
      setIntroText(detail.intro_text);
      setSeoText(detail.seo_text);
      setFaq(detail.faq.map((item) => ({ question: item.question, answer: item.answer })));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не вдалося завантажити тег");
    }
  };

  const save = async () => {
    if (!selected) return;
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const updated = await adminApi.updateTagSeo(selected.id, {
        seo_title: seoTitle,
        seo_description: seoDescription,
        intro_text: introText,
        seo_text: seoText,
        faq: faq.filter((item) => item.question.trim() && item.answer.trim()),
      });
      setSelected(updated);
      setSaved(true);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не вдалося зберегти");
    } finally {
      setSaving(false);
    }
  };

  const updateFaq = (index: number, field: keyof FaqDraft, value: string) => {
    setFaq((prev) => prev.map((item, i) => (i === index ? { ...item, [field]: value } : item)));
  };

  const filtered = tags.filter((tag) => {
    if (groupFilter !== "all" && tag.group !== groupFilter) return false;
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return tag.name.toLowerCase().includes(q) || tag.slug.toLowerCase().includes(q);
  });

  if (selected) {
    return (
      <div className="space-y-4 pb-28">
        <button
          type="button"
          onClick={() => setSelected(null)}
          className="inline-flex min-h-[40px] items-center gap-1 rounded-full bg-surface px-3 text-sm font-bold text-ink"
        >
          <ChevronLeft className="h-4 w-4" /> Усі теги
        </button>

        <div className="rounded-3xl border border-line bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <div>
              <h2 className="font-display text-lg font-bold text-ink">{selected.name}</h2>
              <p className="text-xs text-muted">
                /kulky/{selected.slug} · {selected.product_count} товарів
              </p>
            </div>
            <span
              className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${
                selected.is_indexable ? "bg-emerald-100 text-emerald-900" : "bg-neutral-200 text-neutral-700"
              }`}
            >
              {selected.is_indexable ? "Індексується" : "Не індексується"}
            </span>
          </div>

          <div className="mt-4 space-y-3">
            <Field label="SEO-заголовок (до 160)" value={seoTitle} onChange={setSeoTitle} />
            <Field label="SEO-опис (до 300)" value={seoDescription} onChange={setSeoDescription} />
            <div>
              <label className="text-xs font-semibold text-muted">Вступ (над товарами)</label>
              <textarea
                rows={2}
                value={introText}
                onChange={(e) => setIntroText(e.target.value)}
                className="mt-1 w-full rounded-xl border border-line bg-surface p-3 text-sm text-ink focus:border-rose focus:outline-none"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-muted">
                SEO-текст (унікальний, 150–300 слів)
              </label>
              <textarea
                rows={8}
                value={seoText}
                onChange={(e) => setSeoText(e.target.value)}
                placeholder="Опишіть підбірку: кому підходить, що входить, як замовити..."
                className="mt-1 w-full rounded-xl border border-line bg-surface p-3 text-sm text-ink focus:border-rose focus:outline-none"
              />
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-muted">FAQ</label>
                <button
                  type="button"
                  onClick={() => setFaq((prev) => [...prev, { question: "", answer: "" }])}
                  className="inline-flex items-center gap-1 rounded-full bg-surface px-2.5 py-1 text-[11px] font-bold text-rose-deep"
                >
                  <Plus className="h-3 w-3" /> Питання
                </button>
              </div>
              <div className="mt-2 space-y-2">
                {faq.map((item, index) => (
                  <div key={index} className="rounded-xl border border-line bg-surface p-2.5">
                    <input
                      type="text"
                      value={item.question}
                      onChange={(e) => updateFaq(index, "question", e.target.value)}
                      placeholder="Питання"
                      className="min-h-[38px] w-full rounded-lg border border-line bg-white px-2.5 text-xs font-semibold text-ink"
                    />
                    <textarea
                      rows={2}
                      value={item.answer}
                      onChange={(e) => updateFaq(index, "answer", e.target.value)}
                      placeholder="Відповідь"
                      className="mt-1.5 w-full rounded-lg border border-line bg-white p-2.5 text-xs text-ink"
                    />
                    <button
                      type="button"
                      onClick={() => setFaq((prev) => prev.filter((_, i) => i !== index))}
                      className="mt-1 inline-flex items-center gap-1 text-[11px] font-semibold text-rose-deep"
                    >
                      <Trash2 className="h-3 w-3" /> Видалити
                    </button>
                  </div>
                ))}
                {faq.length === 0 && (
                  <p className="text-xs italic text-muted">Немає питань — додайте перше.</p>
                )}
              </div>
            </div>
          </div>

          {error && <p className="text-xs font-semibold text-red-600">{error}</p>}
          {saved && <p className="text-xs font-semibold text-emerald-700">Збережено ✓</p>}

          <button
            type="button"
            disabled={saving}
            onClick={() => void save()}
            className="mt-4 flex min-h-[50px] w-full items-center justify-center gap-2 rounded-full bg-ink text-sm font-bold text-white shadow-pop disabled:opacity-50"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Зберегти
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 pb-24">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-muted" />
          <input
            type="search"
            placeholder="Пошук тегу..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="min-h-[44px] w-full rounded-full border border-line bg-white pl-10 pr-4 text-sm text-ink focus:border-rose focus:outline-none"
          />
        </div>
        <button
          type="button"
          onClick={() => setCreatingTag((v) => !v)}
          className="inline-flex min-h-[44px] shrink-0 items-center gap-1 rounded-full bg-ink px-4 text-xs font-bold text-white"
        >
          <Plus className="h-4 w-4" /> Новий тег
        </button>
      </div>

      {/* Group filter chips */}
      <div className="-mx-4 flex gap-1.5 overflow-x-auto px-4 pb-1 [scrollbar-width:none]">
        <button
          type="button"
          onClick={() => setGroupFilter("all")}
          className={`min-h-[34px] shrink-0 rounded-full px-3 text-xs font-bold transition ${
            groupFilter === "all"
              ? "bg-rose-deep text-white"
              : "border border-line bg-white text-ink"
          }`}
        >
          Усі ({tags.length})
        </button>
        {Object.entries(GROUP_LABELS).map(([key, label]) => {
          const count = tags.filter((t) => t.group === key).length;
          return (
            <button
              key={key}
              type="button"
              onClick={() => setGroupFilter(key)}
              className={`min-h-[34px] shrink-0 rounded-full px-3 text-xs font-bold transition ${
                groupFilter === key
                  ? "bg-rose-deep text-white"
                  : "border border-line bg-white text-ink"
              }`}
            >
              {label} ({count})
            </button>
          );
        })}
      </div>

      {creatingTag && (
        <form
          onSubmit={(e) => void handleCreateTag(e)}
          className="space-y-2.5 rounded-3xl border border-accent bg-white p-4 shadow-sm"
        >
          <div className="text-xs font-bold text-rose-deep">
            Створити новий тег / SEO-підбірку
          </div>
          <div className="grid grid-cols-3 gap-2">
            <select
              value={newGroup}
              onChange={(e) => setNewGroup(e.target.value)}
              className="min-h-[42px] rounded-xl border border-line bg-surface px-2.5 text-xs font-semibold text-ink"
            >
              {Object.entries(GROUP_LABELS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Назва (напр. Пастельні)"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="min-h-[42px] rounded-xl border border-line bg-surface px-3 text-xs"
            />
            <input
              type="text"
              placeholder="slug (pastelni)"
              value={newSlug}
              onChange={(e) => setNewSlug(e.target.value)}
              className="min-h-[42px] rounded-xl border border-line bg-surface px-3 text-xs"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setCreatingTag(false)}
              className="rounded-full px-3 py-1.5 text-xs text-muted"
            >
              Скасувати
            </button>
            <button
              type="submit"
              className="rounded-full bg-ink px-4 py-1.5 text-xs font-bold text-white"
            >
              Створити і заповнити SEO
            </button>
          </div>
        </form>
      )}

      {error && <p className="text-xs font-semibold text-red-600">{error}</p>}

      {loading ? (
        <div className="flex justify-center py-10">
          <Loader2 className="h-6 w-6 animate-spin text-rose-deep" />
        </div>
      ) : (
        <div className="space-y-2.5">
          {filtered.map((tag) => (
            <button
              key={tag.id}
              type="button"
              onClick={() => void openTag(tag.slug)}
              className="flex w-full items-center gap-3 rounded-3xl border border-line bg-white p-3.5 text-left shadow-sm transition active:scale-[0.99]"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="truncate font-display text-sm font-bold text-ink">{tag.name}</span>
                  <span className="rounded-full bg-accent-soft/70 px-2 py-0.5 text-[10px] font-semibold text-rose-deep">
                    {GROUP_LABELS[tag.group] ?? tag.group}
                  </span>
                </div>
                <p className="mt-0.5 text-[11px] text-muted">
                  /kulky/{tag.slug} · {tag.product_count} товарів
                </p>
              </div>
              <span
                className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                  tag.is_indexable ? "bg-emerald-100 text-emerald-900" : "bg-neutral-200 text-neutral-700"
                }`}
              >
                {tag.is_indexable ? "✓ SEO" : "Ні"}
              </span>
            </button>
          ))}
          {filtered.length === 0 && (
            <p className="py-8 text-center text-sm text-muted">Немає тегів.</p>
          )}
        </div>
      )}
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <label className="text-xs font-semibold text-muted">{label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 min-h-[44px] w-full rounded-xl border border-line bg-surface px-3 text-sm text-ink focus:border-rose focus:outline-none"
      />
    </div>
  );
}
