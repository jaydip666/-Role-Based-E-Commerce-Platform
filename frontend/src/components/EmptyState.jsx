export default function EmptyState({ title = "Nothing here yet", message, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-gray-300 bg-white px-6 py-16 text-center">
      <p className="text-base font-semibold text-gray-800">{title}</p>
      {message && <p className="text-sm text-gray-500">{message}</p>}
      {action}
    </div>
  );
}
