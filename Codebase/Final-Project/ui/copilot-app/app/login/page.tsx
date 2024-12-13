"use client"; // Required for Next.js client components

import { useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const router = useRouter();

  const handleLogin = async () => {
    try {
      const response = await fetch("http://3.95.250.248:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setMessage(`Login failed: ${errorData.detail}`);
        return;
      }

      const data = await response.json();
      localStorage.setItem("token", data.access_token); // Store the token
      setMessage("Login successful! Redirecting...");
      setTimeout(() => {
        router.push("/"); // Redirect to the homepage or dashboard
      }, 2000);
    } catch (error) {
      setMessage("An error occurred during login.");
      console.error(error);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Log In</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
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
        onClick={handleLogin}
        className="bg-green-500 text-white px-4 py-2 rounded"
      >
        Log In
      </button>
      <p
        className="text-blue-400 mt-4 cursor-pointer underline"
        onClick={() => router.push("/signup")} // Navigate to signup page
      >
        Don't have an account? Sign Up
      </p>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
}
