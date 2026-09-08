export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-gray-500">
        <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
          <p>&copy; {new Date().getFullYear()} Mini-Shopping. Assessment Based project.</p>
          <p>Built with React, Flask &amp; MongoDB.</p>
        </div>
      </div>
    </footer>
  );
}
