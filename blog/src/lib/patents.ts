import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

const contentDirectory = path.join(process.cwd(), 'src/content/patents');

export interface Patent {
  slug: string;
  title: string;
  original_title: string;
  date: string;
  category: string;
  image?: string;
  original_link: string;
  source: string;
  applicant: string;
  content: string;
}

export function getAllPatents(): Patent[] {
  if (!fs.existsSync(contentDirectory)) {
    return [];
  }
  const fileNames = fs.readdirSync(contentDirectory);
  const allPatentsData = fileNames
    .filter((fileName) => fileName.endsWith('.md'))
    .map((fileName) => {
      const slug = fileName.replace(/\.md$/, '');
      const fullPath = path.join(contentDirectory, fileName);
      const fileContents = fs.readFileSync(fullPath, 'utf8');
      const { data, content } = matter(fileContents);

      return {
        slug,
        title: data.title || 'Untitled',
        original_title: data.original_title || '',
        date: data.date || '',
        category: data.category || '',
        image: data.image || '',
        original_link: data.original_link || '',
        source: data.source || '',
        applicant: data.applicant || '不明',
        content,
      } as Patent;
    });

  return allPatentsData.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getPatentBySlug(slug: string): Patent | null {
  const fullPath = path.join(contentDirectory, `${slug}.md`);
  if (!fs.existsSync(fullPath)) return null;

  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const { data, content } = matter(fileContents);

  return {
    slug,
    title: data.title || 'Untitled',
    original_title: data.original_title || '',
    date: data.date || '',
    category: data.category || '',
    image: data.image || '',
    original_link: data.original_link || '',
    source: data.source || '',
    applicant: data.applicant || '不明',
    content,
  } as Patent;
}
