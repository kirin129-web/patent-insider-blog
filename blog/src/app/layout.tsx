import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import Script from "next/script";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  metadataBase: new URL("https://patent-summary-blog.vercel.app"),
  title: {
    default: "Patent Insider | 最新特許を未来予測に",
    template: "%s | Patent Insider",
  },
  description:
    "Apple、Google、Sonyなど大手企業の最新特許をAIが要約。難しい技術を小学生でもわかるレベルで解説し、未来のガジェットや技術トレンドを先取りします。",
  keywords: [
    "特許",
    "特許要約",
    "最新特許",
    "Apple特許",
    "Google特許",
    "未来のガジェット",
    "テクノロジー",
    "AI",
    "VR",
    "ロボット",
    "EV",
  ],
  openGraph: {
    type: "website",
    locale: "ja_JP",
    siteName: "Patent Insider",
    title: "Patent Insider | 最新特許を未来予測に",
    description:
      "大手企業の最新特許をAIが超わかりやすく要約。未来のテクノロジーを先取り！",
  },
  twitter: {
    card: "summary_large_image",
    title: "Patent Insider | 最新特許を未来予測に",
    description:
      "大手企業の最新特許をAIが超わかりやすく要約。未来のテクノロジーを先取り！",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className={`${inter.variable} ${outfit.variable}`}>
      <head>
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-NL759TFZCP"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-NL759TFZCP');
          `}
        </Script>
      </head>
      <body className="antialiased bg-slate-50 text-slate-900 font-sans min-h-screen">
        {/* Navigation */}
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200/60">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <a href="/" className="flex items-center gap-2.5 group">
                <div className="w-9 h-9 bg-gradient-to-br from-indigo-600 to-amber-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200/50 group-hover:shadow-indigo-300/70 transition-shadow">
                  <span className="text-white font-bold text-sm">P</span>
                </div>
                <span className="text-xl font-bold tracking-tight">
                  <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-700 to-slate-800">
                    Patent
                  </span>{" "}
                  <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-600 to-amber-500">
                    Insider
                  </span>
                </span>
              </a>
              <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
                <a
                  href="/"
                  className="hover:text-indigo-600 transition-colors"
                >
                  最新記事
                </a>
                <a
                  href="/categories"
                  className="hover:text-indigo-600 transition-colors"
                >
                  カテゴリー
                </a>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-gradient-to-b from-slate-50 to-slate-100 border-t border-slate-200 py-16 mt-20">
          <div className="max-w-7xl mx-auto px-4 text-center space-y-4">
            <div className="flex items-center justify-center gap-2 mb-2">
              <div className="w-7 h-7 bg-gradient-to-br from-indigo-600 to-amber-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xs">P</span>
              </div>
              <span className="font-bold text-slate-900">Patent Insider</span>
            </div>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              最新の特許情報をAIが要約し、未来のテクノロジーを先取り。
              <br />
              あなたの「なるほど！」を毎日お届けします。
            </p>
            <p className="text-xs text-slate-400">
              © 2026 Patent Insider. All rights reserved.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
