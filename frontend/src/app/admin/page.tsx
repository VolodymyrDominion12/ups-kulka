"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  BarChart3,
  Camera,
  LayoutGrid,
  Loader2,
  Lock,
  LogOut,
  ShoppingBag,
  Tags,
} from "lucide-react";
import {
  adminApi,
  getStoredAdminToken,
  ProductOut,
  setStoredAdminToken,
  TagOut,
} from "@/shared/api/admin";
import { QuickPublishTab } from "@/features/admin/QuickPublishTab";
import { OrdersSalonTab } from "@/features/admin/OrdersSalonTab";
import { CatalogManageTab } from "@/features/admin/CatalogManageTab";
import { AnalyticsMarketingTab } from "@/features/admin/AnalyticsMarketingTab";
import { TagSeoTab } from "@/features/admin/TagSeoTab";

type AdminTab = "orders" | "publish" | "catalog" | "analytics" | "tags";

export default function AdminMobilePage() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loggingIn, setLoggingIn] = useState(false);

  const [activeTab, setActiveTab] = useState<AdminTab>("publish");
  const [tags, setTags] = useState<TagOut[]>([]);
  const [products, setProducts] = useState<ProductOut[]>([]);
  const [prefillFromOrder, setPrefillFromOrder] = useState<{
    name: string;
    priceUah: number;
  } | null>(null);

  const bootstrapAdminData = useCallback(async () => {
    try {
      await adminApi.me();
      setAuthenticated(true);
      const [tagList, productPage] = await Promise.all([
        adminApi.listTags(),
        adminApi.listAdminProducts({ limit: 100 }),
      ]);
      setTags(tagList);
      setProducts(productPage.items);
    } catch {
      setAuthenticated(false);
    }
  }, []);

  useEffect(() => {
    const token = getStoredAdminToken();
    if (!token) {
      setAuthenticated(false);
      return;
    }
    void bootstrapAdminData();
  }, [bootstrapAdminData]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError(null);
    setLoggingIn(true);
    try {
      await adminApi.login(password);
      setPassword("");
      await bootstrapAdminData();
    } catch (err) {
      setLoginError(
        err instanceof Error ? err.message : "Невірний пароль адміністратора"
      );
    } finally {
      setLoggingIn(false);
    }
  };

  const handleLogout = () => {
    setStoredAdminToken(null);
    setAuthenticated(false);
  };

  if (authenticated === null) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg">
        <Loader2 className="h-8 w-8 animate-spin text-rose-deep" />
      </div>
    );
  }

  if (!authenticated) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-5 py-10">
        <div className="rounded-3xl border border-line bg-white p-6 shadow-card">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-accent-soft text-rose-deep">
            <Lock className="h-6 w-6" />
          </div>
          <h1 className="mt-4 text-center font-display text-2xl font-extrabold text-ink">
            УПС! Кулька · Салон
          </h1>
          <p className="mt-1 text-center text-xs text-muted">
            Мобільна адмін-панель для швидкої публікації композицій з камери та
            аналітики продажів
          </p>

          <form onSubmit={handleLogin} className="mt-6 space-y-4">
            <div>
              <label className="text-xs font-bold text-muted">
                Пароль адміністратора
              </label>
              <input
                type="password"
                required
                autoFocus
                placeholder="Введіть пароль..."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 min-h-[50px] w-full rounded-2xl border border-line bg-surface px-4 text-base font-bold text-ink focus:border-rose focus:outline-none"
              />
            </div>

            {loginError && (
              <div className="rounded-2xl bg-red-50 px-3.5 py-2.5 text-xs font-semibold text-red-700">
                {loginError}
              </div>
            )}

            <button
              type="submit"
              disabled={loggingIn}
              className="flex min-h-[50px] w-full items-center justify-center rounded-full bg-ink text-sm font-bold text-white shadow-pop transition active:scale-[0.99]"
            >
              {loggingIn ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Увійти в адмін-панель"
              )}
            </button>
          </form>
        </div>
      </main>
    );
  }

  return (
    <div className="mx-auto min-h-screen max-w-xl bg-bg">
      {/* Compact Sticky Salon Header */}
      <header className="sticky top-0 z-30 flex items-center justify-between border-b border-line bg-bg/90 px-4 py-3 backdrop-blur">
        <div className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-rose-deep text-sm text-white">
            🎈
          </span>
          <div>
            <h1 className="font-display text-sm font-extrabold leading-tight text-ink">
              УПС! Кулька · Салон
            </h1>
            <p className="text-[11px] text-muted">
              {activeTab === "publish" && "Експрес-публікація з камери"}
              {activeTab === "orders" && "Дошка замовлень салону"}
              {activeTab === "catalog" && `Каталог (${products.length})`}
              {activeTab === "analytics" && "Аналітика та маркетинг"}
              {activeTab === "tags" && "SEO підбірки"}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          title="Вийти"
          className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-line bg-white text-muted hover:text-ink"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </header>

      {/* Main Content Area */}
      <main className="px-4 pt-4">
        {activeTab === "publish" && (
          <QuickPublishTab
            tags={tags}
            prefillName={prefillFromOrder?.name}
            prefillPriceUah={prefillFromOrder?.priceUah}
            onPublished={(created) => {
              setProducts((prev) => [created, ...prev]);
              setPrefillFromOrder(null);
            }}
            onTagsChanged={() => {
              void adminApi.listTags().then(setTags);
            }}
          />
        )}

        {activeTab === "orders" && (
          <OrdersSalonTab
            products={products}
            onShootFromOrder={(prefill) => {
              setPrefillFromOrder(prefill);
              setActiveTab("publish");
            }}
          />
        )}

        {activeTab === "catalog" && (
          <CatalogManageTab
            products={products}
            onProductUpdated={(updated) =>
              setProducts((prev) =>
                prev.map((p) => (p.id === updated.id ? updated : p))
              )
            }
          />
        )}

        {activeTab === "analytics" && <AnalyticsMarketingTab />}

        {activeTab === "tags" && <TagSeoTab />}
      </main>

      {/* Sticky Bottom Thumb Navigation Bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 mx-auto max-w-xl border-t border-line bg-white/95 px-2 py-1.5 backdrop-blur">
        <div className="grid grid-cols-5 gap-1">
          <button
            type="button"
            onClick={() => setActiveTab("orders")}
            className={`flex min-h-[48px] flex-col items-center justify-center rounded-2xl text-[11px] font-bold transition ${
              activeTab === "orders"
                ? "bg-accent-soft/70 text-rose-deep"
                : "text-muted"
            }`}
          >
            <ShoppingBag className="h-4 w-4" />
            <span className="mt-0.5">Замовлення</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("publish")}
            className={`flex min-h-[48px] flex-col items-center justify-center rounded-2xl text-[11px] font-bold transition ${
              activeTab === "publish"
                ? "bg-rose-deep text-white shadow-sm"
                : "text-ink"
            }`}
          >
            <Camera className="h-4 w-4" />
            <span className="mt-0.5">+ Зняти фото</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("catalog")}
            className={`flex min-h-[48px] flex-col items-center justify-center rounded-2xl text-[11px] font-bold transition ${
              activeTab === "catalog"
                ? "bg-accent-soft/70 text-rose-deep"
                : "text-muted"
            }`}
          >
            <LayoutGrid className="h-4 w-4" />
            <span className="mt-0.5">Каталог</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("analytics")}
            className={`flex min-h-[48px] flex-col items-center justify-center rounded-2xl text-[11px] font-bold transition ${
              activeTab === "analytics"
                ? "bg-accent-soft/70 text-rose-deep"
                : "text-muted"
            }`}
          >
            <BarChart3 className="h-4 w-4" />
            <span className="mt-0.5">Аналітика</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("tags")}
            className={`flex min-h-[48px] flex-col items-center justify-center rounded-2xl text-[11px] font-bold transition ${
              activeTab === "tags"
                ? "bg-accent-soft/70 text-rose-deep"
                : "text-muted"
            }`}
          >
            <Tags className="h-4 w-4" />
            <span className="mt-0.5">Теги</span>
          </button>
        </div>
      </nav>
    </div>
  );
}
