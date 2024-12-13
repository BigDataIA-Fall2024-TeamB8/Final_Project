"use client";

import { useRouter } from "next/navigation";

export default function SignupButton() {
  const router = useRouter();

  const handleSignupClick = () => {
    router.push("/signup"); // Navigate to the signup page
  };

  return (
    <button
      onClick={handleSignupClick}
      className="bg-green-500 text-white px-4 py-2 rounded w-full"
    >
      Sign Up
    </button>
  );
}
