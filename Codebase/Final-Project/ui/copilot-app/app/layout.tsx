"use client"; // Required for client-side rendering

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
import "./globals.css";
import "@copilotkit/react-ui/styles.css";
import { ReactNode, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import SidebarButtons from "./components/SideBarButtons";

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    router.push("/login"); // Redirect to login page
  };

  return (
    <html lang="en">
      <body className="bg-black text-white">
        <CopilotKit runtimeUrl="/api/copilotkit">
          <div className="flex h-screen">
            {/* Sidebar */}
            <aside className="w-1/4 p-6 bg-red-700 shadow-lg border-r border-gray-800 flex flex-col">
              <header className="mb-6">
                <h1 className="text-3xl font-bold text-white">TED Explorer</h1>
                <p className="text-sm text-gray-300 mt-2">
                  Explore, learn, and take notes on TED Talks.
                </p>
              </header>

              {/* Conditionally render sidebar buttons */}
              {isAuthenticated && <SidebarButtons />}

              {/* Authentication Buttons */}
              <div className="mt-auto">
                {isAuthenticated ? (
                  <button
                    className="bg-red-500 text-white px-4 py-2 rounded mt-4 w-full"
                    onClick={handleLogout}
                  >
                    Log Out
                  </button>
                ) : (
                  <>
                    <button
                      className="bg-blue-500 text-white px-4 py-2 rounded mb-4 w-full"
                      onClick={() => router.push("/login")}
                    >
                      Log In
                    </button>
                    <button
                      className="bg-green-500 text-white px-4 py-2 rounded w-full"
                      onClick={() => router.push("/signup")}
                    >
                      Sign Up
                    </button>
                  </>
                )}
              </div>
            </aside>

            {/* Main Content */}
            <main className="w-3/4 p-6 bg-black overflow-y-auto">
              {children}
            </main>

            {/* Chatbot Popup */}
            {isAuthenticated && (
              <div className="absolute bottom-4 right-4 space-y-4">
                <CopilotPopup
                  instructions="You are a chatbot assistant for TED Talks. Answer user queries based on the data available in the backend."
                  labels={{
                    title: "TED Chatbot",
                    initial: "Hello! Ask me anything about TED Talks!",
                  }}
                />
              </div>
            )}
          </div>
        </CopilotKit>
      </body>
    </html>
  );
}
