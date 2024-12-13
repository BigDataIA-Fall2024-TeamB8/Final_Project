"use client";

import { useRouter, usePathname } from "next/navigation";
import { useState } from "react";

export default function SidebarButtons() {
  const router = useRouter();
  const pathname = usePathname(); // Get current path
  const [isLoading, setIsLoading] = useState(false);

  const navigateToPlaybooks = () => {
    setIsLoading(true);
    router.push("/playbook");
  };

  const navigateToHome = () => {
    setIsLoading(true);
    router.push("/");
  };

  const handleCompareTalksClick = () => {
    router.push("/compare");
  };

  const isActive = (path: string) => pathname === path;

  return (
    <div className="flex flex-col space-y-4 mt-6">
      <button
        className={`px-4 py-2 rounded text-white hover:bg-red-900 ${
          isActive("/") ? "bg-red-900" : "bg-red-800"
        }`}
        onClick={navigateToHome}
        disabled={isLoading}
      >
        Home
      </button>
      <button
        className={`px-4 py-2 rounded text-white hover:bg-red-900 ${
          isActive("/playbooks") ? "bg-red-900" : "bg-red-800"
        }`}
        onClick={navigateToPlaybooks}
        disabled={isLoading}
      >
        Saved Playbooks
      </button>
      <button
        className={`px-4 py-2 rounded text-white hover:bg-red-900 ${
          isActive("/compare-talks") ? "bg-red-900" : "bg-red-800"
        }`}
        onClick={handleCompareTalksClick}
        disabled={isLoading}
      >
        Compare Talks
      </button>
    </div>
  );
}
