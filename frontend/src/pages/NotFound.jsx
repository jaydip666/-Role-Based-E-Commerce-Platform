import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-4 px-4 py-24 text-center">
      <h1 className="text-4xl font-bold text-gray-900">404</h1>
      <p className="text-gray-500">The page you&apos;re looking for doesn&apos;t exist.</p>
      <Link to="/" className="btn-primary">Back to home</Link>
    </div>
  );
}
