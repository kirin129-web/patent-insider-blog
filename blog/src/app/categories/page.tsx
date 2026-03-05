import { getAllPatents } from "@/lib/patents";
import Link from "next/link";
import { ChevronRight, Tag } from "lucide-react";

const CATEGORY_COLORS: Record<
    string,
    { bg: string; text: string; border: string; icon: string }
> = {
    AI: {
        bg: "bg-purple-50",
        text: "text-purple-700",
        border: "border-purple-200",
        icon: "🤖",
    },
    "VR/AR": {
        bg: "bg-blue-50",
        text: "text-blue-700",
        border: "border-blue-200",
        icon: "🥽",
    },
    ロボティクス: {
        bg: "bg-rose-50",
        text: "text-rose-700",
        border: "border-rose-200",
        icon: "🦾",
    },
    "EV・バッテリー": {
        bg: "bg-green-50",
        text: "text-green-700",
        border: "border-green-200",
        icon: "🔋",
    },
    スマートフォン: {
        bg: "bg-sky-50",
        text: "text-sky-700",
        border: "border-sky-200",
        icon: "📱",
    },
    ヘルスケア: {
        bg: "bg-emerald-50",
        text: "text-emerald-700",
        border: "border-emerald-200",
        icon: "🏥",
    },
    コンピューティング: {
        bg: "bg-indigo-50",
        text: "text-indigo-700",
        border: "border-indigo-200",
        icon: "💻",
    },
    通信: {
        bg: "bg-cyan-50",
        text: "text-cyan-700",
        border: "border-cyan-200",
        icon: "📡",
    },
    ディスプレイ: {
        bg: "bg-amber-50",
        text: "text-amber-700",
        border: "border-amber-200",
        icon: "🖥️",
    },
};

const DEFAULT_COLOR = {
    bg: "bg-slate-50",
    text: "text-slate-700",
    border: "border-slate-200",
    icon: "💡",
};

export default function CategoriesPage() {
    const patents = getAllPatents();

    const categories: Record<string, typeof patents> = {};
    patents.forEach((patent) => {
        const cat = patent.category || "その他";
        if (!categories[cat]) categories[cat] = [];
        categories[cat].push(patent);
    });

    const sortedCategories = Object.entries(categories).sort(
        (a, b) => b[1].length - a[1].length
    );

    return (
        <div className="space-y-12">
            <header className="text-center space-y-4">
                <h1 className="text-5xl font-extrabold tracking-tight text-slate-900">
                    カテゴリー
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-amber-500">
                        一覧
                    </span>
                </h1>
                <p className="text-xl text-slate-500 max-w-2xl mx-auto">
                    気になるジャンルから最新特許を探してみよう！
                </p>
            </header>

            {sortedCategories.length === 0 ? (
                <div className="text-center py-20 text-slate-400">
                    まだカテゴリーがありません。記事が追加されるとここに表示されます。
                </div>
            ) : (
                <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                    {sortedCategories.map(([category, catPatents]) => {
                        const colors = CATEGORY_COLORS[category] || DEFAULT_COLOR;
                        return (
                            <div
                                key={category}
                                className={`rounded-3xl border ${colors.border} ${colors.bg} p-6 space-y-4 hover:shadow-md transition-shadow`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className="text-2xl">{colors.icon}</span>
                                        <h2 className={`text-xl font-bold ${colors.text}`}>
                                            {category}
                                        </h2>
                                    </div>
                                    <span
                                        className={`text-sm font-semibold ${colors.text} opacity-70`}
                                    >
                                        {catPatents.length}件
                                    </span>
                                </div>
                                <ul className="space-y-3">
                                    {catPatents.slice(0, 5).map((patent) => (
                                        <li key={patent.slug}>
                                            <Link
                                                href={`/patents/${patent.slug}`}
                                                className={`group flex items-start gap-2 text-sm text-slate-700 hover:${colors.text} transition-colors`}
                                            >
                                                <ChevronRight className="w-4 h-4 mt-0.5 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                                                <span className="line-clamp-2 leading-relaxed">
                                                    {patent.title}
                                                </span>
                                            </Link>
                                        </li>
                                    ))}
                                    {catPatents.length > 5 && (
                                        <li
                                            className={`text-xs font-medium ${colors.text} opacity-60 pt-1`}
                                        >
                                            + 他 {catPatents.length - 5}件の特許
                                        </li>
                                    )}
                                </ul>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
