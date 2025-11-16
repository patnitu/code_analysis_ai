import React, { useState } from "react";
import "./App.css";
import { uploadFileAPI, analyzeQueryAPI } from "./api";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);

    if (!file) return;

    setUploadStatus("Uploading...");
    setResponse("");

    try {
      const res = await uploadFileAPI(file);
      setUploadStatus("Upload successful ✔");
    } catch (err) {
      setUploadStatus("Upload failed ❌");
    }
  };

  const handleSubmit = async () => {
    if (!query.trim()) {
      alert("Please enter a query");
      return;
    }

    setLoading(true);
    setResponse("");

    try {
      const res = await analyzeQueryAPI(query);

      if (typeof res === "object") {
        setResponse(JSON.stringify(res, null, 2));
      } else {
        setResponse(res);
      }
    } catch (err) {
      setResponse("Error: " + err.message);
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h2>AI Code Analysis</h2>

      <div className="section">
        <label>Upload Code File:</label>
        <input type="file" onChange={handleFileChange} />
        {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
      </div>

      <div className="section">
        <label>Enter your Prompt:</label>
        <input
          type="text"
          className="prompt-box"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something about your code..."
        />
      </div>

      <button className="submit-btn" onClick={handleSubmit} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      <div className="section">
        <label>AI Response:</label>
        <textarea
          className="response-box"
          value={response}
          readOnly
        ></textarea>
      </div>
    </div>
  );
}

export default App;
