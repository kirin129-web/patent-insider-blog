import { getAllPatents } from '@/lib/patents';
import { MetadataRoute } from 'next';

const SITE_URL = 'https://patent-summary-blog.vercel.app';

export default function sitemap(): MetadataRoute.Sitemap {
    const patents = getAllPatents();

    const patentEntries = patents.map((patent) => ({
        url: `${SITE_URL}/patents/${patent.slug}`,
        lastModified: new Date(patent.date),
        changeFrequency: 'weekly' as const,
        priority: 0.8,
    }));

    return [
        {
            url: SITE_URL,
            lastModified: new Date(),
            changeFrequency: 'daily',
            priority: 1.0,
        },
        {
            url: `${SITE_URL}/categories`,
            lastModified: new Date(),
            changeFrequency: 'daily',
            priority: 0.7,
        },
        ...patentEntries,
    ];
}
