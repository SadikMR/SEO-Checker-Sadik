/**
 * TypeScript types mirroring the backend AuditResponse schema.
 * Keep in sync with backend/schemas/audit.py and backend/schemas/seo_data.py.
 */

export interface RedirectInfo {
  url: string;
  status: number;
}

export interface CategoryScore {
  category: string;
  score: number;
  max_score: number;
  label: string;
}

export interface ScoreSummary {
  overall_score: number;
  categories: CategoryScore[];
}

export interface AuditIssue {
  rule_id: string;
  category: string;
  severity: "critical" | "warning" | "info" | "pass";
  message: string;
  value?: string | null;
}

export interface AuditRecommendation {
  rule_id: string;
  category: string;
  severity: "critical" | "warning" | "info" | "pass";
  message: string;
}

export interface MetaTagData {
  title: string | null;
  title_length: number | null;
  description: string | null;
  description_length: number | null;
  canonical: string | null;
}

export interface HeadingData {
  h1: string[];
  h2: string[];
  h3: string[];
  h4: string[];
  h5: string[];
  h6: string[];
  h1_count: number;
}

export interface OpenGraphData {
  og_title: string | null;
  og_description: string | null;
  og_image: string | null;
  og_url: string | null;
  og_type: string | null;
  og_site_name: string | null;
}

export interface TwitterCardData {
  card: string | null;
  title: string | null;
  description: string | null;
  image: string | null;
  site: string | null;
}

export interface ImageData {
  total_images: number;
  images_with_alt: number;
  images_without_alt: number;
  alt_texts: string[];
}

export interface LinkData {
  total_links: number;
  internal_links: number;
  external_links: number;
  nofollow_links: number;
}

export interface RobotsData {
  meta_robots: string | null;
  x_robots_tag: string | null;
}

export interface StructuredDataInfo {
  has_json_ld: boolean;
  json_ld_types: string[];
  has_microdata: boolean;
  microdata_types: string[];
}

export interface RawSEOData {
  meta: MetaTagData;
  headings: HeadingData;
  open_graph: OpenGraphData;
  twitter_card: TwitterCardData;
  images: ImageData;
  links: LinkData;
  robots: RobotsData;
  structured_data: StructuredDataInfo;
}

export interface AuditResponse {
  input_url: string;
  final_url: string;
  redirects: RedirectInfo[];
  scores: ScoreSummary;
  results: AuditIssue[];
  recommendations: AuditRecommendation[];
  raw_data: RawSEOData;
}

export interface AuditErrorResponse {
  detail: string;
  error_code?: string | null;
}
