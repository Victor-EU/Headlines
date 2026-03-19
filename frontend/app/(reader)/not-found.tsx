import Link from "next/link";

export default function ReaderNotFound() {
  return (
    <div className="py-16 text-center space-y-4">
      <h1 className="text-xl font-semibold text-primary">
        We couldn&apos;t find that page
      </h1>
      <Link href="/" className="text-accent hover:underline text-sm">
        Go to homepage
      </Link>
    </div>
  );
}
