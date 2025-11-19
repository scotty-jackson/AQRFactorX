/**
 * Footer component
 */
import React from 'react';
import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <h3 className="text-white font-semibold text-lg mb-4">About</h3>
            <p className="text-sm text-gray-400">
              AQR Factor Explorer provides interactive tools for analyzing factor performance
              using publicly available AQR research data.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-semibold text-lg mb-4">Explore</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/factors" className="text-sm hover:text-white transition-colors">
                  All Factors
                </Link>
              </li>
              <li>
                <Link href="/compare" className="text-sm hover:text-white transition-colors">
                  Compare Factors
                </Link>
              </li>
              <li>
                <Link href="/analytics" className="text-sm hover:text-white transition-colors">
                  Analytics
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-white font-semibold text-lg mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://www.aqr.com/Insights/Datasets"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm hover:text-white transition-colors"
                >
                  AQR Data Library
                </a>
              </li>
              <li>
                <a
                  href="https://www.aqr.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm hover:text-white transition-colors"
                >
                  AQR Capital
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-white font-semibold text-lg mb-4">Legal</h3>
            <p className="text-xs text-gray-400">
              This site displays research data for educational purposes only.
              Not investment advice. Past performance does not guarantee future results.
            </p>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm text-gray-400">
          <p>
            © {currentYear} AQR Factor Explorer. Data provided by AQR Capital Management.
          </p>
        </div>
      </div>
    </footer>
  );
}
