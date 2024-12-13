"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import jsPDF from "jspdf";

interface Playbook {
  id: string;
  title: string;
  speaker: string;
  url: string;
  content: string;
}

export default function PlaybookDetailsPage() {
  const { id } = useParams();
  const [playbook, setPlaybook] = useState<Playbook | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchPlaybook = async () => {
      if (!id) {
        console.error("ID is undefined. Cannot fetch playbook.");
        setError("Invalid playbook ID.");
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `http://3.95.250.248:8000/playbooks/${id}`
        );
        if (!response.ok)
          throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        setPlaybook(data);
      } catch (err) {
        console.error("Error fetching playbook details:", err);
        setError("Failed to load playbook details.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchPlaybook();
  }, [id]);

  const handleDownloadPDF = () => {
    if (!playbook) return;

    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text(playbook.title, 10, 10);
    doc.setFontSize(12);
    doc.text(`Speaker: ${playbook.speaker}`, 10, 20);
    doc.text(`Link: ${playbook.url}`, 10, 30);
    doc.setFontSize(14);
    doc.text("Report", 10, 40);
    doc.setFontSize(12);
    const lines = doc.splitTextToSize(playbook.content, 180);
    doc.text(lines, 10, 50);
    doc.save(`${playbook.title.replace(/\s+/g, "_")}.pdf`);
  };

  if (isLoading) {
    return (
      <p className="text-center text-gray-500">Loading playbook details...</p>
    );
  }

  if (error) {
    return <p className="text-center text-red-500">{error}</p>;
  }

  if (!playbook) {
    return (
      <p className="text-center text-gray-500">
        No details available for this playbook.
      </p>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Title */}
      <h1 className="text-4xl font-bold text-gray-900 mb-6">
        {playbook.title}
      </h1>
      {/* Speaker */}
      <p className="text-lg text-gray-700 mb-4 font-medium">
        <span className="font-bold">Speaker:</span> {playbook.speaker}
      </p>
      {/* Video Embed */}
      <div className="mb-6">
        <iframe
          src={playbook.url}
          className="w-full h-72 rounded-lg shadow-lg"
          frameBorder="0"
          allowFullScreen
          title={playbook.title}
        ></iframe>
      </div>
      {/* Notes */}
      <div className="p-6 bg-gray-100 rounded-lg shadow-inner">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800">Report</h2>
        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
          {playbook.content}
        </p>
      </div>
      {/* Download Button */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={handleDownloadPDF}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-lg shadow-md"
        >
          Download Playbook as PDF
        </button>
      </div>
    </div>
  );
}
