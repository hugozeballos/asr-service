'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function useAuthGuard(): boolean {
  const router = useRouter()
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const token = localStorage.getItem('access')
    console.log('🔒 useAuthGuard - token encontrado:', token)

    if (!token) {
      router.replace('/login')
    } else {
      setIsReady(true)
    }
  }, [router])

  return isReady
}
