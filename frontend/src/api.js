// small helper so every component calls the backend the same way
async function call(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
  return res.json();
}

export const getConsent = () => call("GET", "/api/consent");
export const acceptConsent = () => call("POST", "/api/consent");
export const getProfile = () => call("GET", "/api/profile");
export const saveProfile = (p) => call("PUT", "/api/profile", p);
export const askQuestion = (text) => call("POST", "/api/ask", { text });
export const getHistory = () => call("GET", "/api/history");
export const sendFeedback = (history_id, rating) => call("POST", "/api/feedback", { history_id, rating });
export const deleteMyData = () => call("DELETE", "/api/my-data");
