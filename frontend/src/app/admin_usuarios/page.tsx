'use client'

import { useEffect, useState } from 'react'
import useAuthGuard from '@/hooks/useAuthGuard'

interface User {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
  is_active: boolean;
}

export default function GestionUsuarios() {
  const [users, setUsers] = useState<User[]>([])
  const [newUsername, setNewUsername] = useState('')
  const [newPassword, setNewPassword] = useState('')
    // Nuevos estados para is_staff e is_active
  const [newIsStaff, setNewIsStaff] = useState(false)
  const [newIsActive, setNewIsActive] = useState(true)
  const isReady = useAuthGuard()

  useEffect(() => {
    if (!isReady) return

    const token = localStorage.getItem("access")
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/users/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    .then(res => res.json())
    .then(data => setUsers(data))
    .catch(err => console.error("Error al cargar usuarios:", err))
  }, [isReady])

  const crearUsuario = async () => {
    const token = localStorage.getItem("access")
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/users/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: newUsername, password: newPassword, is_staff: false, is_active: true})
    })

    if (res.ok) {
      alert("✅ Usuario creado")
      setNewUsername("")
      setNewPassword("")
      setNewIsStaff(false)   
      setNewIsActive(true)
    } else {
      alert("❌ Error al crear usuario")
    }
  }

  const eliminarUsuario = async (id: number) => {
    const token = localStorage.getItem("access")
    await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/users/${id}/`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    setUsers(users.filter(u => u.id !== id))
  }

  if (!isReady) return null

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Gestión de Usuarios</h1>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Nombre de usuario"
          value={newUsername}
          onChange={e => setNewUsername(e.target.value)}
          className="border p-2 mr-2"
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={newPassword}
          onChange={e => setNewPassword(e.target.value)}
          className="border p-2 mr-2"
        />
        {/* Checkboxes para is_staff e is_active */}
        <label className="mr-4">
          <input
            type="checkbox"
            checked={newIsStaff}
            onChange={e => setNewIsStaff(e.target.checked)}
            className="mr-1"
          />
          Es Staff
        </label>
        <label className="mr-4">
          <input
            type="checkbox"
            checked={newIsActive}
            onChange={e => setNewIsActive(e.target.checked)}
            className="mr-1"
          />
          Está Activo
        </label>

        <button onClick={crearUsuario} className="bg-blue-600 text-white px-4 py-2 rounded">
          ➕ Crear
        </button>
      </div>

      <ul className="space-y-2">
        {users.map(user => (
          <li key={user.id} className="flex justify-between items-center border p-2 rounded">
            <span>{user.username}</span>
            <button onClick={() => eliminarUsuario(user.id)} className="text-red-600 hover:underline">
              Eliminar
            </button>
          </li>
        ))}
      </ul>
    </main>
  )
}
