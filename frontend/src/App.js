import React, { useState } from "react";
import './App.css';  // <-- Import the CSS file

function App() {
  const [file, setFile] = useState(null);
  const [wordLimit, setWordLimit] = useState(20);
  const [altText, setAltText] = useState("");
  const [loading, setLoading] = useState(false);

  // Use environment variable for API base URL
  const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8001";

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Please upload an image");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("word_limit", wordLimit);

    setLoading(true);
    setAltText("");

    try {
      const response = await fetch(`${API_BASE_URL}/generate-alt-text`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setAltText(data.alt_text || "No alt text generated.");
    } catch (error) {
      console.error("Error:", error);
      setAltText("Error: Failed to fetch alt text");
    } finally {
      setLoading(false);
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
