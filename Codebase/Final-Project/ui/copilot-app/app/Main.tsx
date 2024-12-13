"use client";

import SearchBar from "./components/SearchBar";
import TedTalkCard from "./components/TedTalkCard";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface TedTalk {
  title: string;
  speaker: string;
  description: string;
  video_embed_html: string;
  slug: string;
}

export default function Main() {
  const [trendingTalks, setTrendingTalks] = useState<TedTalk[]>([]);
  const [searchResults, setSearchResults] = useState<TedTalk[]>([]);
  const [query, setQuery] = useState("");
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login"); // Redirect if not logged in
    }
  }, [router]);

  useEffect(() => {
    const fetchTrendingTalks = async () => {
      try {
        const res = await fetch("http://3.95.250.248:8000/trending");
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        if (data.talks) {
          const talks = data.talks.map((talk: any) => ({
            title: talk.title,
            speaker: talk.speakers,
            description: talk.description,
            video_embed_html: talk.video_embed_html || talk.videoEmbedHtml,
            slug: talk.slug,
          }));
          setTrendingTalks(talks);
        }
      } catch (err) {
        console.error("Error fetching trending talks:", err);
      }
    };

    fetchTrendingTalks();
  }, []);

  const handleSearch = async () => {
    if (query.trim()) {
      try {
        const response = await fetch("http://3.95.250.248:8000/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query }),
        });
        if (!response.ok)
          throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        if (data.results) {
          const results = data.results.map((talk: any) => ({
            title: talk.title,
            speaker: talk.speakers,
            description: talk.description,
            video_embed_html: talk.video_embed_html || talk.videoEmbedHtml,
            slug: talk.slug,
          }));
          setSearchResults(results);
        }
      } catch (error) {
        console.error("Error fetching search results:", error);
      }
    }
  };

  const handleCardClick = (talk: TedTalk) => {
    const { title, speaker, description, video_embed_html, slug } = talk;
    if (!slug) {
      console.error("Missing slug in talk:", talk);
      return;
    }
    const queryString = new URLSearchParams({
      title,
      speaker,
      description,
      video_embed_html,
      slug,
    }).toString();
    router.push(`/tedtalk?${queryString}`);
  };

  const handleBackToTrending = () => setSearchResults([]);

  const talksToDisplay =
    searchResults.length > 0 ? searchResults : trendingTalks;

  return (
    <div className="p-4">
      <h1 className="text-4xl font-bold mb-6 text-white">Discover TED Talks</h1>
      <SearchBar query={query} setQuery={setQuery} onSearch={handleSearch} />
      <div className="mt-6">
        <h2 className="text-2xl font-semibold text-red-500 mb-4">
          {searchResults.length > 0 ? "Search Results" : "Trending Talks"}
        </h2>
        {searchResults.length > 0 && (
          <button
            className="bg-gray-500 text-white px-4 py-2 rounded mb-4"
            onClick={handleBackToTrending}
          >
            Back to Trending
          </button>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {talksToDisplay.map((talk, index) => (
            <TedTalkCard
              key={index}
              talk={talk}
              onClick={() => handleCardClick(talk)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
