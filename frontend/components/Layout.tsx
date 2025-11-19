/**
 * Main layout component
 */
import React, { ReactNode } from 'react';
import Head from 'next/head';
import NavBar from './NavBar';
import Footer from './Footer';

interface LayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
}

export default function Layout({
  children,
  title = 'AQR Factor Explorer',
  description = 'Explore and analyze AQR factor performance data with interactive charts and analytics'
}: LayoutProps) {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />

        {/* Open Graph / Social Media */}
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:type" content="website" />

        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
      </Head>

      <div className="min-h-screen flex flex-col bg-gray-50">
        <NavBar />

        {/* Ad Slot - Top Banner */}
        {/* Google AdSense or other ad code would go here */}
        <div id="ad-slot-top" className="bg-gray-100 border-b border-gray-200 h-24 flex items-center justify-center text-gray-400 text-sm">
          {/* Ad Banner Placeholder - 728x90 */}
        </div>

        <main className="flex-grow container mx-auto px-4 py-8 max-w-7xl">
          <div className="flex gap-6">
            {/* Main Content */}
            <div className="flex-grow">
              {children}
            </div>

            {/* Sidebar Ad Slot */}
            <aside className="hidden lg:block w-64 flex-shrink-0">
              <div
                id="ad-slot-sidebar"
                className="sticky top-24 bg-gray-100 border border-gray-200 rounded-lg h-[600px] flex items-center justify-center text-gray-400 text-sm"
              >
                {/* Sidebar Ad Placeholder - 300x600 */}
              </div>
            </aside>
          </div>
        </main>

        {/* Ad Slot - Bottom Banner */}
        <div id="ad-slot-bottom" className="bg-gray-100 border-t border-gray-200 h-24 flex items-center justify-center text-gray-400 text-sm">
          {/* Ad Banner Placeholder - 728x90 */}
        </div>

        <Footer />
      </div>
    </>
  );
}
