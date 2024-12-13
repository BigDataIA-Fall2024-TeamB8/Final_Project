"use client";

import { useMemo } from "react";

interface TedTalk {
  title: string;
  description: string;
  speaker: string;
  video_embed_html: string;
}

interface TedTalkCardProps {
  talk: TedTalk;
  onClick: () => void;
}

export default function TedTalkCard({ talk, onClick }: TedTalkCardProps) {
  const videoEmbed = useMemo(
    () => (
      <div
        className="mt-4"
        dangerouslySetInnerHTML={{ __html: talk.video_embed_html }}
      ></div>
    ),
    [talk.video_embed_html]
  );

  return (
    <div
      className="bg-gray-800 text-white p-4 rounded-lg shadow-md cursor-pointer"
      onClick={onClick}
    >
      <h3 className="text-xl font-bold">{talk.title}</h3>
      {videoEmbed}
    </div>
  );
}
