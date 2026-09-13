export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6 py-16">
      <div className="max-w-2xl text-center">
        <p className="mb-3 text-sm font-medium uppercase tracking-[0.2em] text-violet-600">
          Portfolio Preview
        </p>
        <h1 className="text-4xl font-semibold tracking-tight text-zinc-950">
          Rahul Bisht
        </h1>
        <p className="mt-4 text-lg leading-8 text-zinc-600">
          This demo shows how the portfolio chatbot widget appears on your site.
          Visitors can ask about your B.Tech background, skills, and projects.
        </p>
        <p className="mt-3 text-sm text-zinc-500">
          Try the greeting bubble in the bottom-right corner.
        </p>
      </div>
    </main>
  );
}
