import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-6 text-center">
      <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full bg-accent-soft text-3xl">
        🎈
      </div>
      <h1 className="font-display text-3xl font-bold text-rose-deep">
        УПС! Кулька
      </h1>
      <p className="mt-2 text-sm text-muted">
        Інтернет-магазин повітряних кульок та мобільний кабінет салону
      </p>
      <Link
        href="/admin"
        className="mt-6 inline-flex min-h-[48px] w-full items-center justify-center rounded-full bg-ink px-6 py-3.5 text-base font-semibold text-white shadow-pop transition active:scale-[0.99]"
      >
        Відкрити мобільну адмінку салону →
      </Link>
    </main>
  );
}
