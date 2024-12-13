"use client";

interface SearchBarProps {
  query: string;
  setQuery: (query: string) => void;
  onSearch: () => void;
}

export default function SearchBar({
  query,
  setQuery,
  onSearch,
}: SearchBarProps) {
  return (
    <div className="flex items-center space-x-4">
      <input
        type="text"
        placeholder="Search TED Talks..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="flex-grow p-2 border border-gray-500 rounded-md text-black"
      />
      <button
        onClick={onSearch}
        className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
      >
        Search
      </button>
    </div>
  );
}
