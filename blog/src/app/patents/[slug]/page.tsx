import { getPatentBySlug, getAllPatents } from "@/lib/patents";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import {
    Calendar,
    Building2,
    ExternalLink,
    ArrowLeft,
    Lightbulb,
} from "lucide-react";
import Link from "next/link";
import { Metadata } from "next";

export async function generateStaticParams() {
    const patents = getAllPatents();
    return patents.map((patent) => ({
        slug: patent.slug,
    }));
}

export async function generateMetadata({
    params,
}: {
    params: Promise<{ slug: string }>;
}): Promise<Metadata> {
    const { slug } = await params;
    const patent = getPatentBySlug(slug);
    if (!patent) return {};

    const description = patent.content
        .replace(/[#*\n]/g, " ")
        .trim()
        .substring(0, 160);

    return {
        title: patent.title,
        description,
        openGraph: {
            title: patent.title,
            description,
            type: "article",
            publishedTime: patent.date,
            images: patent.image
                ? [{ url: patent.image, width: 800, height: 450 }]
                : [],
        },
        twitter: {
            card: "summary_large_image",
            title: patent.title,
            description,
            images: patent.image ? [patent.image] : [],
        },
    };
}

export default async function PatentPage({
    params,
}: {
    params: Promise<{ slug: string }>;
}) {
    const { slug } = await params;
    const patent = getPatentBySlug(slug);

    if (!patent) {
        notFound();
    }

    const jsonLd = {
        "@context": "https://schema.org",
        "@type": "Article",
        headline: patent.title,
        datePublished: patent.date,
        author: {
            "@type": "Organization",
            name: patent.applicant || "Unknown",
        },
        publisher: {
            "@type": "Organization",
            name: "Patent Insider",
        },
        description: patent.content
            .replace(/[#*\n]/g, " ")
            .trim()
            .substring(0, 160),
        ...(patent.image ? { image: patent.image } : {}),
    };

    return (
        <>
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />
            <article className="max-w-3xl mx-auto space-y-12">
                <Link
                    href="/"
                    className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-indigo-600 transition-colors group"
                >
                    <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
                    記事一覧に戻る
                </Link>

                <header className="space-y-6">
                    {patent.image && (
                        <div className="w-full h-80 md:h-96 rounded-3xl overflow-hidden shadow-lg border border-slate-100">
                            <img
                                src={patent.image}
                                alt={patent.title}
                                className="w-full h-full object-cover"
                            />
                        </div>
                    )}

                    <div className="flex flex-wrap items-center gap-3">
                        {patent.category && (
                            <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider">
                                {patent.category}
                            </span>
                        )}
                        <span className="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-bold tracking-wider">
                            ⚡ {patent.source?.split(" - ")[1] || patent.source}
                        </span>
                        <div className="flex items-center gap-1 text-sm text-slate-500">
                            <Calendar className="w-4 h-4" />
                            <span>{patent.date}</span>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 leading-tight">
                            {patent.title}
                        </h1>
                        {patent.original_title && (
                            <p className="text-slate-400 text-sm italic font-medium">
                                Original: {patent.original_title}
                            </p>
                        )}
                    </div>

                    <div className="flex items-center gap-4 py-4 border-y border-slate-100">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-indigo-100 to-amber-100 rounded-full flex items-center justify-center">
                                <Building2 className="w-5 h-5 text-indigo-600" />
                            </div>
                            <div className="text-sm">
                                <p className="font-semibold text-slate-800">
                                    {patent.applicant || "不明"}
                                </p>
                                <p className="text-slate-500">出願企業</p>
                            </div>
                        </div>
                        {patent.original_link && (
                            <a
                                href={patent.original_link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="ml-auto inline-flex items-center px-4 py-2 text-sm font-semibold text-slate-700 hover:text-indigo-600 transition-colors border border-slate-200 rounded-xl hover:border-indigo-200"
                            >
                                原文を読む{" "}
                                <ExternalLink className="w-4 h-4 ml-2" />
                            </a>
                        )}
                    </div>
                </header>

                {/* Article body */}
                <div
                    className="prose prose-slate prose-indigo lg:prose-xl max-w-none 
          prose-headings:font-bold prose-headings:text-slate-900
          prose-p:text-slate-600 prose-p:leading-relaxed
          prose-strong:text-slate-900 prose-strong:font-bold
          prose-li:text-slate-600
          prose-img:rounded-3xl prose-img:shadow-lg"
                >
                    <ReactMarkdown>{patent.content}</ReactMarkdown>
                </div>

                {/* Footer card */}
                <footer className="mt-16 pt-8 border-t border-slate-200">
                    <div className="bg-gradient-to-br from-indigo-50 to-amber-50 rounded-3xl p-8 space-y-4 shadow-inner border border-indigo-100/50">
                        <h3 className="text-xl font-bold text-indigo-900 flex items-center gap-2">
                            <Lightbulb className="w-5 h-5 text-amber-500" />
                            About This Summary
                        </h3>
                        <p className="text-indigo-800/80 leading-relaxed text-sm">
                            この記事は最新の特許情報を基に、AI（Gemini）が要約・解説したものです。
                            専門的な特許文書を、誰でも楽しめるように分かりやすく翻訳しています。
                            正確な内容については、必ず原文の特許文書をご確認ください。
                        </p>
                    </div>
                </footer>
            </article>
        </>
    );
}
