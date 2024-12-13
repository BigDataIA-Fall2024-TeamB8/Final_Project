"use client";

import { useRouter } from "next/navigation";

export default function LoginButton() {
  const router = useRouter();

  const handleLoginClick = () => {
    router.push("/login"); // Navigate to the login page
  };

  return (
    <button
      onClick={handleLoginClick}
      className="bg-blue-500 text-white px-4 py-2 rounded w-full"
    >
      Log In
    </button>
  );
}
