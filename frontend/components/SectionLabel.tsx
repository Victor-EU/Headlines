export function SectionLabel({ label }: { label: string }) {
  if (!label) return null;

  return (
    <div className="mt-8 mb-4">
      <h3 className="text-section-label text-section-label uppercase font-sans">
        {label}
      </h3>
      <hr className="mt-2" />
    </div>
  );
}
