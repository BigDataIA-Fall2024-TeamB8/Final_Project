"use client";

import { useState } from "react";

export default function CustomChatbot() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>(
    []
  );
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to the chat
    setMessages((prev) => [...prev, { role: "user", content: input }]);

    try {
      const response = await fetch("/api/copilotkit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error from backend:", errorText);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "An error occurred. Please try again.",
          },
        ]);
        return;
      }

      const result = await response.json();

      // Add assistant's response to the chat
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.result },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "An error occurred. Please try again." },
      ]);
    }

    setInput(""); // Clear input field
  };

  return (
    <div className="p-4 bg-gray-800 text-white rounded-lg shadow-md w-96">
      <div className="h-64 overflow-y-auto mb-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`p-2 my-1 rounded ${
              msg.role === "user"
                ? "bg-blue-500 text-white self-end"
                : "bg-gray-500 text-white self-start"
            }`}
          >
            {msg.content}
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          type="text"
          className="flex-grow p-2 rounded-l border border-gray-500 text-black"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") sendMessage();
          }}
        />
        <button
          onClick={sendMessage}
          className="bg-blue-500 text-white p-2 rounded-r"
        >
          Send
        </button>
      </div>
    </div>
  );
}
