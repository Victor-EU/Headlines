const PUBLICATIONS = [
  "Financial Times",
  "Bloomberg",
  "The Wall Street Journal",
  "The Verge",
  "Stratechery",
  "Harvard Business Review",
  "MIT Sloan Management Review",
];

export function Footer() {
  return (
    <footer className="border-t border-rule py-6 mt-12">
      <p className="text-meta text-muted text-center">
        {PUBLICATIONS.join(" · ")}
      </p>
      <p className="text-meta text-muted text-center mt-1">headlines.example.com</p>
    </footer>
  );
}
