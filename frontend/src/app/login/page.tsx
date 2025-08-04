'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    })

    if (res.ok) {
      const data = await res.json()
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      router.push('/grabar') // Redirigir a la página principal o protegida
    } else {
      setError('Usuario o contraseña incorrectos.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-2xl shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Iniciar Sesión</h1>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Usuario</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full mt-1 p-2 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full mt-1 p-2 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200"
            />
          </div>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200"
          >
            Ingresar
          </button>
        </form>
      </div>
    </div>
  )
}