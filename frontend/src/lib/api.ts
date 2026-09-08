/**
 * AIMD Police Cyber Cell API Client
 * Connects frontend dashboard to FastAPI backend (http://localhost:8000)
 * Developer: Daksh Walia, B.Tech AIML
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface MediaAnalysisResponse {
  status: string;
  file_name: string;
  sha256_hash: string;
  ai_probability_score: number;
  verdict: string;
  suspected_engine: string;
  timestamp: string;
  job_id: string;
  media_type: string;
  file_size_bytes: number;
  forensic_details?: {
    chain_of_custody_verified: boolean;
    hash_algorithm: string;
    section_65b_ready?: boolean;
  };
}

export interface AudioAnalysisResponse {
  job_id: string;
  status: string;
  original_filename: string;
  sha256_original: string;
  voice_authenticity: string;
  confidence_score: number;
  duration_seconds: number;
  sample_rate_hz: number;
  segments_analyzed: number;
  model_version: string;
  completed_at: string;
  forensic_signals: Array<{
    name: string;
    score: number;
    description: string;
  }>;
}

export interface EvidenceItem {
  job_id: string;
  filename: string;
  size_bytes: number;
  sha256: string;
  url: string;
}

export interface PhishingCheckResponse {
  domain: string;
  status: string;
  risk_score: number;
  domain_age_days: number;
  warning_tags: string[];
  report_summary: string;
  cached: boolean;
}

export interface ExtensionScanResponse {
  url: string;
  verdict?: string;
  confidence?: number;
  threat_level: string;
  sha256?: string;
  error?: string;
}

// ──────────────────────────────────────────────────────────
// Helper: Handle Fetch Errors
// ──────────────────────────────────────────────────────────
async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `Server error: ${res.status} ${res.statusText}`;
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        errorMsg = typeof errorJson.detail === "string" 
          ? errorJson.detail 
          : JSON.stringify(errorJson.detail);
      }
    } catch {
      // fallback to status text
    }
    throw new Error(errorMsg);
  }
  return res.json() as Promise<T>;
}

// ──────────────────────────────────────────────────────────
// API Methods
// ──────────────────────────────────────────────────────────

/** Health Check */
export async function checkBackendHealth(): Promise<{ status: string; system: string; mode: string }> {
  const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
  return handleResponse(res);
}

/** Analyze Media File (Image/Video/Audio) */
export async function analyzeMedia(file: File): Promise<MediaAnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/api/v1/analyze/media`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<MediaAnalysisResponse>(res);
}

/** Analyze Synthetic Voice / Audio File */
export async function analyzeAudio(file: File): Promise<AudioAnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/api/v1/analyze/audio`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<AudioAnalysisResponse>(res);
}

/** Fetch Media Analysis Job Result */
export async function getMediaJobResult(jobId: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analyze/media/${jobId}`);
  return handleResponse(res);
}

/** Secure Immutable Evidence Upload */
export async function uploadEvidence(file: File): Promise<MediaAnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/evidence/upload`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<MediaAnalysisResponse>(res);
}

/** List Evidence Files */
export async function listEvidence(): Promise<EvidenceItem[]> {
  const res = await fetch(`${API_BASE_URL}/evidence/list`, { cache: "no-store" });
  return handleResponse<EvidenceItem[]>(res);
}

/** Get Download URL for Evidence File */
export function getEvidenceFileUrl(jobId: string, filename: string): string {
  return `${API_BASE_URL}/evidence/file/${jobId}/${filename}`;
}

/** Generate Section 65B PDF Certificate URL */
export function buildSection65bPdfUrl(params: {
  caseId: string;
  officerBadgeId: string;
  mediaJobId?: string;
  audioJobId?: string;
  officerName?: string;
  notes?: string;
}): string {
  const query = new URLSearchParams({
    officer_badge_id: params.officerBadgeId,
  });
  if (params.mediaJobId) query.append("media_job_id", params.mediaJobId);
  if (params.audioJobId) query.append("audio_job_id", params.audioJobId);
  if (params.officerName) query.append("officer_name", params.officerName);
  if (params.notes) query.append("notes", params.notes);

  return `${API_BASE_URL}/api/v1/cases/${encodeURIComponent(params.caseId)}/pdf?${query.toString()}`;
}

/** Scan Media URL via Extension router */
export async function scanMediaUrl(url: string): Promise<ExtensionScanResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/extension/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return handleResponse<ExtensionScanResponse>(res);
}

/** Phishing & Impersonation Domain Reputation Check */
export async function checkDomainReputation(url: string): Promise<PhishingCheckResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/extension/check-domain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return handleResponse<PhishingCheckResponse>(res);
}

/** Download Extension ZIP URL */
export function getExtensionDownloadUrl(): string {
  return `${API_BASE_URL}/api/v1/extension/download`;
}
