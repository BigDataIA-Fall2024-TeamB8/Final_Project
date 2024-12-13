"use client"; // Required for Next.js client components

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const router = useRouter();

  const handleSignup = async () => {
    try {
      const response = await fetch("http://3.95.250.248:8000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, email }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setMessage(`Signup failed: ${errorData.detail}`);
        return;
      }

      setMessage("Signup successful! Redirecting to login...");
      setTimeout(() => {
        router.push("/login"); // Redirect to login page
      }, 2000);
    } catch (error) {
      setMessage("An error occurred during signup.");
      console.error(error);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Sign Up</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="block w-full mb-2 p-2 border"
      />
      <input
        type="text" // Change to "text" to make email visible
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="block w-full mb-2 p-2 border"
      />
      <input
        type="text" // Change to "text" to make password visible
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="block w-full mb-2 p-2 border"
      />
      <button
        onClick={handleSignup}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Sign Up
      </button>
      <p
        className="text-blue-400 mt-4 cursor-pointer underline"
        onClick={() => router.push("/login")} // Navigate to login page
      >
        Already have an account? Log In
      </p>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
}
