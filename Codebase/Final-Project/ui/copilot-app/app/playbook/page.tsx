"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Playbook {
  id: string; // Unique ID for the playbook
  title: string;
  speaker: string;
  url: string;
}

export default function PlaybookPage() {
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchPlaybooks = async () => {
      try {
        const response = await fetch("http://3.95.250.248:8000/playbooks");
        if (!response.ok)
          throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        setPlaybooks(data.playbooks || []);
      } catch (err: any) {
        console.error("Error fetching playbooks:", err);
        setError("Failed to load playbooks. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchPlaybooks();
  }, []);

  const handleDeletePlaybook = async (id: string) => {
    try {
      const response = await fetch(`http://3.95.250.248:8000/playbooks/${id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);

      setPlaybooks(playbooks.filter((playbook) => playbook.id !== id));
      alert("Playbook deleted successfully!");
    } catch (err: any) {
      console.error("Error deleting playbook:", err);
      alert("Failed to delete playbook. Please try again later.");
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">Saved Playbooks</h1>

      {isLoading ? (
        <p>Loading playbooks...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : playbooks.length === 0 ? (
        <p>No playbooks found.</p>
      ) : (
        <div className="space-y-6">
          {playbooks.map((playbook, index) => (
            <div
              key={index}
              className="p-4 border border-gray-300 rounded bg-gray-800 text-white"
            >
              <h2 className="text-xl font-bold mb-2">{playbook.title}</h2>
              {/* Link to the TED Talk */}
              <p className="mb-2">
                <a
                  href={playbook.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 underline"
                >
                  View TED Talk
                </a>
              </p>
              <div className="space-x-4">
                <button
                  className="bg-blue-500 text-white px-4 py-2 rounded"
                  onClick={() =>
                    router.push(`/playbook/${encodeURIComponent(playbook.id)}`)
                  }
                >
                  View Playbook
                </button>
                <button
                  className="bg-red-500 text-white px-4 py-2 rounded"
                  onClick={() => handleDeletePlaybook(playbook.id)}
                >
                  Delete Playbook
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
