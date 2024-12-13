"use client";

import { useState, useMemo } from "react";
import React from "react";
import jsPDF from "jspdf"; // Import jsPDF for PDF generation

interface TedTalk {
  title: string;
  slug: string;
  video_embed_html: string;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

export default function CompareTedTalks() {
  const [talk1Query, setTalk1Query] = useState("");
  const [talk2Query, setTalk2Query] = useState("");
  const [talk1Results, setTalk1Results] = useState<TedTalk[]>([]);
  const [talk2Results, setTalk2Results] = useState<TedTalk[]>([]);
  const [selectedTalk1, setSelectedTalk1] = useState<TedTalk | null>(null);
  const [selectedTalk2, setSelectedTalk2] = useState<TedTalk | null>(null);
  const [comparisonReport, setComparisonReport] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const searchTalks = async (query: string, setResults: Function) => {
    try {
      const response = await fetch("http://3.95.250.248:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      console.error("Error fetching search results:", err);
      setError("Failed to fetch search results. Please try again.");
    }
  };

  const compareTalks = async () => {
    if (!selectedTalk1 || !selectedTalk2) {
      setError("Please select two TED Talks to compare.");
      return;
    }

    setError(null);
    try {
      const response = await fetch("http://3.95.250.248:8000/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          talk1: selectedTalk1.slug,
          talk2: selectedTalk2.slug,
        }),
      });
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setComparisonReport(data.report || "No comparison report available.");
    } catch (err) {
      console.error("Error comparing talks:", err);
      setError("Failed to generate comparison report. Please try again.");
    }
  };

  const downloadReportAsPDF = () => {
    if (!comparisonReport) return;

    const doc = new jsPDF();
    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text("Comparison Report", 10, 10);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(12);
    const lines = doc.splitTextToSize(comparisonReport, 180); // Wrap text to fit the page
    doc.text(lines, 10, 20);

    doc.save("Comparison_Report.pdf");
  };

  const MemoizedTalkCard = React.memo(
    ({
      talk,
      isSelected,
      onSelect,
    }: {
      talk: TedTalk;
      isSelected: boolean;
      onSelect: () => void;
    }) => (
      <div
        key={talk.slug}
        className={`p-4 rounded-lg shadow-md cursor-pointer ${
          isSelected ? "bg-green-500 text-white" : "bg-gray-800 text-gray-300"
        }`}
        onClick={onSelect}
      >
        <h3 className="text-lg font-bold">{talk.title}</h3>
        <div
          className="mt-2"
          dangerouslySetInnerHTML={{ __html: talk.video_embed_html }}
        ></div>
      </div>
    )
  );

  const memoizedTalk1Results = useMemo(
    () =>
      talk1Results.map((talk) => (
        <MemoizedTalkCard
          key={talk.slug}
          talk={talk}
          isSelected={selectedTalk1?.slug === talk.slug}
          onSelect={() => setSelectedTalk1(talk)}
        />
      )),
    [talk1Results, selectedTalk1]
  );

  const memoizedTalk2Results = useMemo(
    () =>
      talk2Results.map((talk) => (
        <MemoizedTalkCard
          key={talk.slug}
          talk={talk}
          isSelected={selectedTalk2?.slug === talk.slug}
          onSelect={() => setSelectedTalk2(talk)}
        />
      )),
    [talk2Results, selectedTalk2]
  );

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-4">Compare TED Talks</h1>

      {/* Search Section for Talk 1 */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Search for Talk 1</h2>
        <input
          type="text"
          placeholder="Search for TED Talk 1"
          value={talk1Query}
          onChange={(e) => setTalk1Query(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded mb-2"
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded"
          onClick={() => searchTalks(talk1Query, setTalk1Results)}
        >
          Search
        </button>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {memoizedTalk1Results}
        </div>
      </div>

      {/* Search Section for Talk 2 */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Search for Talk 2</h2>
        <input
          type="text"
          placeholder="Search for TED Talk 2"
          value={talk2Query}
          onChange={(e) => setTalk2Query(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded mb-2"
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded"
          onClick={() => searchTalks(talk2Query, setTalk2Results)}
        >
          Search
        </button>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {memoizedTalk2Results}
        </div>
      </div>

      {/* Compare Button */}
      <button
        className="bg-green-500 text-white px-4 py-2 rounded"
        onClick={compareTalks}
        disabled={!selectedTalk1 || !selectedTalk2}
      >
        Compare Talks
      </button>

      {/* Error Message */}
      {error && <p className="text-red-500 mt-4">{error}</p>}

      {/* Comparison Report */}
      {comparisonReport && (
        <div className="mt-6 p-4 border border-gray-300 rounded bg-white shadow-md">
          <h2 className="text-xl font-bold mb-2 text-green-500">
            Comparison Report
          </h2>
          {comparisonReport.split("\n").map((paragraph, index) => (
            <p key={index} className="mb-4 leading-relaxed text-gray-800">
              {paragraph}
            </p>
          ))}
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded mt-4"
            onClick={downloadReportAsPDF}
          >
            Download as PDF
          </button>
        </div>
      )}
    </div>
  );
}
