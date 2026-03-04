import { ThemeProvider } from "./context/ThemeContext"

export default function App() {
  return (
    <ThemeProvider>
      <div className="min-h-screen bg-[#0b0f17] text-white flex items-center justify-center">
        <h1 className="text-3xl font-semibold">
          Kernox Dashboard Initializing...
        </h1>
      </div>
    </ThemeProvider>
  )
}