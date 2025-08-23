import axios from "axios";

const baseURL = process.env.REACT_APP_API_BASE_URL || "";

const apiClient = axios.create({
  baseURL,
});

apiClient.interceptors.request.use((config) => {
  const updatedConfig = { ...config };
  updatedConfig.headers = updatedConfig.headers || {};
  // Demo token; in production, replace with real auth flow
  updatedConfig.headers.Authorization = updatedConfig.headers.Authorization || "Bearer demo";
  return updatedConfig;
});

export default apiClient;


