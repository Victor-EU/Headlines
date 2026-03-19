import Link from "next/link";

export default function RootNotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-4">
        <h1 className="text-xl font-semibold text-primary">Page not found</h1>
        <Link href="/" className="text-accent hover:underline text-sm">
          Go to homepage
        </Link>
      </div>
    </div>
  );
}
