import React, { useState } from "react";
import './App.css';  // <-- Import the CSS file

function App() {
  const [file, setFile] = useState(null);
  const [wordLimit, setWordLimit] = useState(20);
  const [altText, setAltText] = useState("");
  const [loading, setLoading] = useState(false);

  // Use environment variable for API base URL
  const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8001";

  const handleSubmit = async (data) => {
    const formData = new FormData();
    // Ensure the key name matches 'file' in your FastAPI function
    formData.append("file", data.image[0]); 
    formData.append("word_limit", 20);
  
    try {
      const response = await fetch(`${API_BASE_URL}/generate-alt-text`, {
        method: "POST",
        body: formData,
        // Note: Do NOT set Content-Type header manually; the browser does it for FormData
      });
  
      if (!response.ok) throw new Error("Server returned an error");
      
      const result = await response.json();
      setAltText(result.alt_text);
    } catch (err) {
      console.error("Fetch error:", err);
    }
  };

  return (
    <div className="container">
      <h1>Image Alt-Text Generator</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        <label>Word Limit: </label>
        <input
          type="number"
          value={wordLimit}
          onChange={(e) => setWordLimit(e.target.value)}
          min="5"
          max="100"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate Alt Text"}
        </button>
      </form>

      {altText && (
        <div className="alt-text-card">
          <h3>Generated Alt Text:</h3>
          <p>{altText}</p>
        </div>
      )}
    </div>
  );
}

export default App;
