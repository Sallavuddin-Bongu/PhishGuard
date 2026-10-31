const BASE = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export const getToken = () => localStorage.getItem("phishguard_token");
export const setToken = value => localStorage.setItem("phishguard_token", value);
export const clearToken = () => localStorage.removeItem("phishguard_token");

export async function apiRequest(path, options = {}) {
  const token = getToken();
  const response = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers
    }
  });

  const type = response.headers.get("content-type") || "";
  const data = type.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof data === "object" && data
      ? data.detail || data.message || "Request failed"
      : data || "Request failed";
    throw new Error(
      typeof detail === "string" ? detail : JSON.stringify(detail)
    );
  }
  return data;
}
