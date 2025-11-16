// api.js

// -----------------------------
// UPLOAD API
// -----------------------------
export async function uploadFileAPI(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    console.log(" file is uploading");
    const res = await fetch("http://localhost:8000/upload/", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error("Upload failed");

    const data = await res.json();
    return data.message || "File uploaded successfully";
  } catch (err) {
    console.error("Upload error:", err);
    return "Error uploading file.";
  }
}

// -----------------------------
// ANALYZE API
// -----------------------------
export async function analyzeQueryAPI(query) {
  try {
    const res = await fetch("http://localhost:8000/analyze/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    if (!res.ok) throw new Error("Analyze failed");

    const data = await res.json();
    return data.response || "No response received";
  } catch (err) {
    console.error("Analyze error:", err);
    return "Error contacting server.";
  }
}

// -----------------------------
// OLD FUNCTION (NOT USED NOW)
// -----------------------------
// Only keep this if you still want a combined API
export async function sendQueryWithFile(query, file) {
  const formData = new FormData();
  formData.append("query", query);

  if (file) {
    formData.append("file", file);
  }

  try {
    const res = await fetch("http://localhost:5000/analyze", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    return data.response || "No response received";
  } catch (err) {
    console.error(err);
    return "Error contacting server.";
  }
}
