import api from "./axios"

export async function getEndpoints() {
  const response = await api.get("/endpoints")
  return response.data
}