/** Site footer. */

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-auto border-t border-gray-800/80 bg-gray-950/50">
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-2 px-4 py-6 text-center sm:flex-row sm:justify-between sm:text-left">
        <p className="text-sm text-gray-500">Built for Hackathon · Team of 2</p>
        <p className="text-sm text-gray-600">
          &copy; {year} AI Debate Arena. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
