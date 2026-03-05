import { getAllPatents } from "@/lib/patents";
import Link from "next/link";
import { Calendar, ChevronRight, Lightbulb, Search } from "lucide-react";

export default function Home() {
  const patents = getAllPatents();

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <header className="text-center space-y-6 py-4">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-50 border border-indigo-100 rounded-full text-sm font-medium text-indigo-700 mb-2">
          <Lightbulb className="w-4 h-4" />
          毎日更新中！
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 leading-tight">
          未来の
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 via-purple-600 to-amber-500 animate-gradient">
            テクノロジー
          </span>
          を
          <br className="hidden sm:block" />
          先取りしよう
        </h1>
        <p className="text-xl text-slate-500 max-w-2xl mx-auto leading-relaxed">
          Apple・Google・Sonyなど大手企業の最新特許を、
          <br className="hidden sm:block" />
          <span className="font-semibold text-slate-700">
            小学生でもわかるレベル
          </span>
          で解説します。
        </p>
      </header>

      {/* Patent Grid */}
      {patents.length === 0 ? (
        <div className="text-center py-24 bg-gradient-to-b from-slate-50 to-white rounded-3xl border-2 border-dashed border-slate-200">
          <Search className="w-16 h-16 text-slate-300 mx-auto mb-6" />
          <p className="text-slate-500 text-lg font-medium">
            まだ投稿がありません
          </p>
          <p className="text-slate-400 text-sm mt-2">
            最新特許の自動取得をお楽しみに！🚀
          </p>
        </div>
      ) : (
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {patents.map((patent) => (
            <Link
              key={patent.slug}
              href={`/patents/${patent.slug}`}
              className="group bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 flex flex-col h-full card-glow"
            >
              {patent.image && (
                <div className="relative h-48 w-full overflow-hidden">
                  <img
                    src={patent.image}
                    alt={patent.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
                  {/* Category badge on image */}
                  {patent.category && (
                    <div className="absolute top-3 right-3">
                      <span className="px-2.5 py-1 bg-white/90 backdrop-blur-sm text-indigo-700 rounded-lg text-xs font-bold shadow-sm">
                        {patent.category}
                      </span>
                    </div>
                  )}
                </div>
              )}
              <div className="p-6 flex-1 space-y-4">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <span className="px-2 py-1 bg-amber-50 text-amber-700 rounded-lg text-xs font-bold tracking-wider badge-pulse">
                    ⚡ {patent.source?.split(" - ")[1] || patent.source}
                  </span>
                  <div className="flex items-center gap-1 ml-auto text-xs">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{patent.date}</span>
                  </div>
                </div>
                <h2 className="text-lg font-bold text-slate-800 leading-snug group-hover:text-indigo-600 transition-colors line-clamp-2">
                  {patent.title}
                </h2>
                {patent.applicant && patent.applicant !== "不明" && (
                  <p className="text-xs text-slate-400 font-medium">
                    🏢 {patent.applicant}
                  </p>
                )}
              </div>
              <div className="px-6 pb-6 flex items-center text-indigo-600 font-semibold text-sm">
                詳しく読む{" "}
                <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
