'use client'

import { useEffect, useState } from 'react';
import useAuthGuard from '@/hooks/useAuthGuard' 
import Navbar from '@/components/Navbar'



interface TranscriptionData {
  id: string;
  file_name: string;
  audio_url: string;
  transcription: string;
  corrected?: string;
  source: string;
}

export default function VerTranscripciones() {
  const [transcriptions, setTranscriptions] = useState<TranscriptionData[]>([])
  const isReady = useAuthGuard() // ✅ usa el hook
  console.log("🟢 isReady en VerTranscripciones:", isReady)


  useEffect(() => {
    console.log("📥 useEffect ejecutado") // 👈 importante
    if (!isReady) return

    const token = localStorage.getItem("access")
    console.log("🔑 token:", token)
    if (!token) return

    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/list-transcriptions/`, {
        headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
        },
    })
        .then(async res => {
        const data = await res.json()

        console.log("📦 Transcripciones recibidas:", data)

        if (!res.ok) {
            console.error("❌ Error al traer transcripciones:", data)
            return
        }

        setTranscriptions(data)
        })
        .catch(err => console.error("🚨 Error en fetch de transcripciones:", err))
    }, [isReady])

  return (
    <main className="p-6">
      <Navbar />
      <h1 className="text-2xl font-bold mb-4">Transcripciones Guardadas</h1>
      <div className="grid gap-4">
        {transcriptions.map((item) => (
          <div key={item.id} className="border p-4 rounded shadow">
            <p><strong>Transcripción:</strong> {item.transcription}</p>
            {item.corrected && (
              <p><strong>Corrección:</strong> {item.corrected}</p>
            )}
            <audio controls src={item.audio_url} className="mt-2" />
          </div>
        ))}
      </div>
    </main>
  );
}
