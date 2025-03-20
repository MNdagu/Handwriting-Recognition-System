import { useState } from "react";
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  TextField,
  Alert,
} from "@mui/material";
import { CloudUpload as CloudUploadIcon } from "@mui/icons-material";
import axios from "axios";

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
      // Create preview URL
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

      // Upload image
      const response = await axios.post(
        "http://localhost:8000/api/handwritten-texts/",
        formData
      );
      const textId = response.data.id;

      // Process image
      await axios.post(
        `http://localhost:8000/api/handwritten-texts/${textId}/process_image/`
      );

      // Get updated text
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
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Handwriting Decoder
        </Typography>

        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
            }}
          >
            <input
              accept="image/*"
              style={{ display: "none" }}
              id="image-upload"
              type="file"
              onChange={handleFileSelect}
            />
            <label htmlFor="image-upload">
              <Button
                variant="contained"
                component="span"
                startIcon={<CloudUploadIcon />}
              >
                Select Image
              </Button>
            </label>

            {preview && (
              <Box sx={{ mt: 2 }}>
                <img
                  src={preview}
                  alt="Preview"
                  style={{ maxWidth: "100%", maxHeight: "300px" }}
                />
              </Box>
            )}

            {selectedFile && (
              <Button
                variant="contained"
                color="primary"
                onClick={handleUpload}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : "Process Image"}
              </Button>
            )}
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {extractedText && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Extracted Text:
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={6}
              value={extractedText}
              onChange={(e) => setExtractedText(e.target.value)}
              variant="outlined"
            />
          </Paper>
        )}
      </Box>
    </Container>
  );
}

export default App;
