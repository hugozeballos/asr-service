// components/Navbar.tsx
'use client'

import Link from 'next/link'

export default function Navbar() {
  return (
    <nav className="bg-blue-900 text-black px-4 py-3 flex justify-between items-center">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <h1 className="font-bold text-lg">🗣️ ASR App   </h1>
        <div className="flex gap-4">
          <Link href="/grabar" className="hover:underline">Transcribir</Link>
          <Link href="/ver_transcripciones" className="hover:underline">Ver transcripciones</Link>
          <Link href="/admin_usuarios" className="hover:underline">Usuarios</Link>

        </div>
      </div>
    </nav>
  )
}