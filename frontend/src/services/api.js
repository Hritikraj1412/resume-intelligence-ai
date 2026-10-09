
import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await API.post("/api/resume/upload", formData);
  return response.data;
};

export const analyzeResume = async (resumeText, jobDescription) => {
  const response = await API.post("/api/analysis/match", {
    resume_text: resumeText,
    job_description: jobDescription,
  });

  return response.data;
};