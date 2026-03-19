export function Masthead() {
  const today = new Date().toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <header className="flex items-baseline justify-between py-4 md:py-6">
      <h1 className="font-serif text-headline-lead text-primary">Headlines</h1>
      <time className="text-meta text-muted">{today}</time>
    </header>
  );
}
