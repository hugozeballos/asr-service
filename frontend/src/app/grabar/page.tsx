"use client";

import { useState, useRef } from "react";

export default function GrabarPage() {
  const [file, setFile] = useState<File | null>(null);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string>("");
  const [originalTranscript, setOriginalTranscript] = useState<string>("");
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [isConfirmed, setIsConfirmed] = useState<boolean | null>(null);

  const startRecording = async () => {
    recordedChunksRef.current = []; // ← limpia los chunks antes de grabar
    setTranscript("");
    setOriginalTranscript("");
    setAudioURL(null);
    setFile(null);

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        setMediaRecorder(recorder);

        recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
            recordedChunksRef.current.push(e.data); // ← guardamos directamente
        }
        };

        recorder.onstop = () => {
          const blob = new Blob(recordedChunksRef.current, { type: "audio/webm" });
          const f = new File([blob], "grabacion.webm", { type: "audio/webm" });
          setFile(f);
          setAudioURL(URL.createObjectURL(blob));
          setIsRecording(false);
          // ✅ Libera el micrófono
          stream.getTracks().forEach((track) => track.stop());
          // 🧪 Consola para debug
          console.log("🎧 Grabación completa:", f.name, f.type, f.size);
        };

        recorder.start();
        setIsRecording(true);

    } catch (err) {
        console.error("Error al acceder al micrófono", err);
    }
    };

  const stopRecording = () => {
    mediaRecorder?.stop();
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] ?? null;
    setFile(f);
    setTranscript("");
    setAudioURL(f ? URL.createObjectURL(f) : null);
  };

  const onTranscribe = async () => {
    if (!file) return;
    setLoading(true);
    setTranscript("");
    
    try {
      const form = new FormData();
      form.append("file", file);
      const token = localStorage.getItem('access')
      
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/transcribe/`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: form,
        }
      );

      if (!res.ok) throw new Error(`Error ${res.status}`);
      const json = await res.json();
      setTranscript(json.text ?? "");
      setOriginalTranscript(json.text ?? ""); 
    } catch (err) {
      console.error(err);
      setTranscript("❌ Error al transcribir");
    } finally {
      setLoading(false);
      setIsConfirmed(null);
    }
  };

  const onSaveCorrection = async () => {
    if (!file || !originalTranscript || !transcript) {
      alert("Faltan datos para guardar.");
      return;
    }

    const form = new FormData();
    form.append("audio", file);
    form.append("transcription", originalTranscript);
    form.append("corrected_transcription", transcript);

    const token = localStorage.getItem("access");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/upload-audio/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: form,
      });

      if (res.ok) {
        alert("✅ Datos guardados exitosamente.");
      } else {
        alert("❌ Error al guardar los datos.");
      }
    } catch (error) {
      console.error(error);
      alert("❌ Error al guardar los datos.");
    }
  };

  return (
    <main className="min-h-screen bg-white text-gray-800 font-sans py-10 px-4 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold text-blue-600 text-center mb-8">Transcriptor ASR</h1>

      <div className="space-y-6 bg-gray-50 border border-gray-200 p-6 rounded-lg shadow">
        <div>
          <p className="font-medium mb-2">1. Subir archivo de audio</p>
          <input
            type="file"
            accept="audio/*"
            onChange={onFileChange}
            className="block w-full text-sm border border-gray-300 rounded p-2"
          />
        </div>

        <div>
          <p className="font-medium mb-2">2. O grabar directamente:</p>
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
            >
              🎤 Iniciar grabación
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
            >
              ⏹ Detener
            </button>
          )}
          {!file && !isRecording && (
            <p className="text-sm text-gray-500 italic">
              Sube un archivo o graba tu voz para comenzar.
            </p>
          )}
        </div>

        {audioURL && (
          <div>
            <p className="font-medium mb-2">3. Reproduce tu audio</p>
            <audio controls src={audioURL} className="w-full" />
          </div>
        )}

        {file && (
          <div className="text-center">
            <button
              onClick={onTranscribe}
              disabled={loading}
              className={`mt-4 px-6 py-2 rounded font-medium ${
                loading
                  ? "bg-gray-400 cursor-not-allowed text-white"
                  : "bg-green-600 hover:bg-green-700 text-white"
              }`}
            >
              {loading ? "Transcribiendo..." : "Transcribir"}
            </button>
          </div>
        )}

        {transcript && (
          <div>
            <h2 className="text-lg font-semibold mt-6">📝 Transcripción:</h2>

            {isConfirmed === false ? (
              <textarea
                className="w-full mt-2 p-2 border border-gray-300 rounded min-h-[100px]"
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
              />
            ) : (
              <p className="bg-white border border-gray-300 p-3 rounded mt-2 whitespace-pre-wrap">
                {transcript}
              </p>
            )}

            <div className="mt-4 space-x-3">
              {isConfirmed === null && (
                <>
                  <button
                    onClick={() => setIsConfirmed(true)}
                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
                  >
                    ✅ Confirmar
                  </button>
                  <button
                    onClick={() => setIsConfirmed(false)}
                    className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded"
                  >
                    ✏️ Corregir
                  </button>
                </>
              )}

              {isConfirmed === false && (
                <button onClick={onSaveCorrection} className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
                  💾 Guardar corrección
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
