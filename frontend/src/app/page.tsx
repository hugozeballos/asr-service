"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string>("");  // ← Nuevo estado
  const [loading, setLoading] = useState<boolean>(false);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] ?? null;
    setFile(f);
    setTranscript("");
    setAudioURL(f ? URL.createObjectURL(f) : null);
  };

  const onTranscribe = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const form = new FormData();
      form.append("audio", file);

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/transcribe/`,
        {
          method: "POST",
          body: form,
        }
      );

      if (!res.ok) {
        throw new Error(`Error ${res.status}`);
      }

      const json = await res.json();
      setTranscript(json.text ?? "");
    } catch (err) {
      console.error(err);
      setTranscript("❌ Error al transcribir");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h1>ASR PoC</h1>

      <p>1. Selecciona un archivo de audio</p>
      <input type="file" accept="audio/*" onChange={onFileChange} />

      {audioURL && (
        <>
          <p style={{ marginTop: 20 }}>2. Reproduce tu audio:</p>
          <audio controls src={audioURL} style={{ display: "block", marginTop: 8 }} />
        </>
      )}

      {file && (
        <button
          onClick={onTranscribe}
          disabled={loading}
          style={{
            marginTop: 20,
            padding: "8px 16px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Transcribiendo..." : "Transcribir"}
        </button>
      )}

      {transcript && (
        <section style={{ marginTop: 20 }}>
          <h2>Transcripción:</h2>
          <div
            style={{
              whiteSpace: "pre-wrap",
              background: "#f5f5f5",
              padding: 10,
              borderRadius: 4,
            }}
          >
            {transcript}
          </div>
        </section>
      )}
    </main>
  );
}
