"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

interface TedTalk {
  title: string;
  video_embed_html: string;
  slug: string;
}

export default function TedTalkPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const title = searchParams.get("title");
  const videoEmbedHtml = searchParams.get("video_embed_html");
  const slug = searchParams.get("slug");

  const [relatedVideos, setRelatedVideos] = useState<TedTalk[]>([]);
  const [transcript, setTranscript] = useState<string>("");
  const [themes, setThemes] = useState<string[]>([]);
  const [mindMap, setMindMap] = useState<string>(""); // Mind Map URL
  const [isGeneratingMap, setIsGeneratingMap] = useState(false);
  const [downloadLink, setDownloadLink] = useState<string>(""); // Download URL
  const [notes, setNotes] = useState<string>("");

  // Memoize the video embed to prevent unnecessary re-renders
  const videoEmbed = useMemo(() => {
    return (
      <div
        className="mt-4"
        dangerouslySetInnerHTML={{ __html: videoEmbedHtml || "" }}
      ></div>
    );
  }, [videoEmbedHtml]);

  // Memoize the related videos to prevent re-fetching on unrelated state updates
  const memoizedRelatedVideos = useMemo(() => {
    return relatedVideos.map((video, index) => (
      <div key={index} className="border border-gray-300 rounded shadow-md p-4">
        <div
          className="mb-4"
          dangerouslySetInnerHTML={{ __html: video.video_embed_html }}
        ></div>
        <a
          href={`https://www.ted.com/talks/${video.slug}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-500 hover:underline block text-center font-bold"
        >
          {video.title}
        </a>
      </div>
    ));
  }, [relatedVideos]);

  // Fetch Themes and Transcript
  useEffect(() => {
    if (!slug) {
      console.error("No slug provided for fetching data.");
      return;
    }

    const fetchThemes = async () => {
      try {
        const response = await fetch("http://3.95.250.248:8000/themes", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ transcript: slug }),
        });

        if (!response.ok)
          throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        setThemes(data.themes || []);
      } catch (error) {
        console.error("Error fetching themes:", error);
      }
    };

    const fetchTranscript = async () => {
      try {
        const response = await fetch(
          `http://3.95.250.248:8000/full_transcript?slug=${slug}`
        );
        if (!response.ok)
          throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        setTranscript(data.transcript || "Transcript not available.");
      } catch (error) {
        console.error("Error fetching transcript:", error);
        setTranscript("Failed to fetch transcript.");
      }
    };

    fetchThemes();
    fetchTranscript();
  }, [slug]);

  // Fetch Related Videos
  useEffect(() => {
    if (!slug) return;

    const fetchRelatedVideos = async () => {
      try {
        const response = await fetch(
          `http://3.95.250.248:8000/related?slug=${slug}`
        );
        if (!response.ok)
          throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        setRelatedVideos(data.talks || []);
      } catch (error) {
        console.error("Error fetching related videos:", error);
      }
    };

    fetchRelatedVideos();
  }, [slug]);

  const handleMindMapClick = async () => {
    if (!slug) {
      console.error("No slug provided for mind map generation.");
      return;
    }

    setIsGeneratingMap(true);
    try {
      const response = await fetch(
        `http://3.95.250.248:8000/mind_map?slug=${slug}`
      );
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setDownloadLink(url);
      setMindMap(url);
    } catch (error) {
      console.error("Error generating mind map:", error);
      setMindMap("Failed to generate mind map.");
    } finally {
      setIsGeneratingMap(false);
    }
  };

  const saveToPlaybook = async () => {
    if (!slug || !title) {
      alert("Missing required information to save the playbook.");
      return;
    }

    try {
      const response = await fetch(
        "http://3.95.250.248:8000/generate_playbook",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            slug,
            url: `https://www.ted.com/talks/${slug}`,
            notes,
            title,
          }),
        }
      );

      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      alert("Playbook saved successfully!");
    } catch (error) {
      console.error("Error saving playbook:", error);
      alert("Failed to save playbook. Please try again later.");
    }
  };

  return (
    <div className="p-4">
      <button
        className="bg-gray-500 text-white px-4 py-2 rounded mb-4"
        onClick={() => router.back()}
      >
        Back to Search
      </button>

      <h1 className="text-3xl font-bold mb-4">{title}</h1>
      {videoEmbed}

      {/* Themes Section */}
      <div className="mt-6">
        <h2 className="text-xl font-bold mb-4">Themes</h2>
        {themes.length > 0 ? (
          <ul className="list-disc pl-6 text-white">
            {themes.map((theme, index) => (
              <li key={index} className="text-white">
                {theme}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-white">No themes found.</p>
        )}
      </div>

      {/* Notes Section */}
      <div className="mt-6">
        <h2 className="text-xl font-bold mb-2">Take Notes Here</h2>
        <textarea
          placeholder="Take notes here..."
          className="w-full p-4 border border-gray-300 rounded text-black"
          rows={6}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        ></textarea>
        <div className="mt-4 space-x-4">
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded"
            onClick={saveToPlaybook}
          >
            Save to Playbook
          </button>
          <button
            className="bg-green-500 text-white px-4 py-2 rounded"
            onClick={handleMindMapClick}
          >
            Create Mind Map
          </button>
        </div>
      </div>

      {/* Transcript Section */}
      <div className="mt-6">
        <h2 className="text-xl font-bold mb-2">Transcript</h2>
        <textarea
          readOnly
          className="w-full p-4 border border-gray-300 rounded text-black bg-gray-100"
          rows={10}
          value={transcript}
        ></textarea>
      </div>

      {/* Mind Map Section */}
      <div className="mt-6">
        <h2 className="text-xl font-bold mb-2">Mind Map</h2>
        {isGeneratingMap ? (
          <p>Generating mind map, please wait...</p>
        ) : mindMap ? (
          <>
            <img
              src={mindMap}
              alt="Generated Mind Map"
              className="mt-4 border border-gray-300 rounded"
            />
            <a
              href={downloadLink}
              download="mind_map.png"
              className="bg-blue-500 text-white px-4 py-2 rounded mt-4 inline-block"
            >
              Download Mind Map
            </a>
          </>
        ) : (
          <p>No mind map generated yet.</p>
        )}
      </div>

      {/* Related Videos Section */}
      <div className="mt-6">
        <h2 className="text-xl font-bold mb-4">Related Videos</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {memoizedRelatedVideos}
        </div>
      </div>
    </div>
  );
}
