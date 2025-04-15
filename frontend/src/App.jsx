import { useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [extractedText, setExtractedText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);

      const response = await axios.post(
        "http://localhost:8000/api/handwritten-texts/",
        formData
      );
      const textId = response.data.id;

      await axios.post(
        `http://localhost:8000/api/handwritten-texts/${textId}/process_image/`
      );

      const updatedResponse = await axios.get(
        `http://localhost:8000/api/handwritten-texts/${textId}/`
      );
      setExtractedText(updatedResponse.data.extracted_text);
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "An error occurred while processing the image"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 bg-light">
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container">
          <a className="navbar-brand" href="#">
            <i className="bi bi-pencil-square me-2"></i>
            Handwriting Decoder
          </a>
        </div>
      </nav>

      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-8">
            <div className="card shadow-sm mb-4">
              <div className="card-body">
                <h5 className="card-title mb-4">Upload Handwritten Text</h5>

                <div className="text-center mb-4">
                  <input
                    accept="image/*"
                    className="d-none"
                    id="image-upload"
                    type="file"
                    onChange={handleFileSelect}
                  />
                  <label
                    htmlFor="image-upload"
                    className="btn btn-primary btn-lg"
                  >
                    <i className="bi bi-cloud-upload me-2"></i>
                    Select Image
                  </label>
                </div>

                {preview && (
                  <div className="text-center mb-4">
                    <div className="position-relative d-inline-block">
                      <img
                        src={preview}
                        alt="Preview"
                        className="img-fluid rounded shadow-sm"
                        style={{ maxHeight: "300px" }}
                      />
                      {selectedFile && (
                        <button
                          className="btn btn-success position-absolute bottom-0 start-50 translate-middle-x mb-3"
                          onClick={handleUpload}
                          disabled={loading}
                        >
                          {loading ? (
                            <>
                              <span
                                className="spinner-border spinner-border-sm me-2"
                                role="status"
                                aria-hidden="true"
                              ></span>
                              Processing...
                            </>
                          ) : (
                            <>
                              <i className="bi bi-gear me-2"></i>
                              Process Image
                            </>
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {error && (
              <div
                className="alert alert-danger alert-dismissible fade show"
                role="alert"
              >
                {error}
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setError(null)}
                ></button>
              </div>
            )}

            {extractedText && (
              <div className="card shadow-sm">
                <div className="card-body">
                  <h5 className="card-title mb-3">Extracted Text</h5>
                  <div className="form-group">
                    <textarea
                      className="form-control"
                      rows="6"
                      value={extractedText}
                      onChange={(e) => setExtractedText(e.target.value)}
                      style={{ resize: "vertical" }}
                    ></textarea>
                  </div>
                  <div className="mt-3">
                    <button
                      className="btn btn-outline-primary"
                      onClick={() =>
                        navigator.clipboard.writeText(extractedText)
                      }
                    >
                      <i className="bi bi-clipboard me-2"></i>
                      Copy to Clipboard
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <footer className="footer mt-auto py-3 bg-light">
        <div className="container text-center">
          <span className="text-muted">
            © 2024 Handwriting Decoder. All rights reserved.
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
