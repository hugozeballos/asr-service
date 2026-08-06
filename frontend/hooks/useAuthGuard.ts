'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

/**
 * Redirects to /login if no access token is in localStorage.
 * Returns true once the check has run and the token was found, so callers
 * can render `null` until then instead of flashing protected content.
 */
export default function useAuthGuard(): boolean {
  const router = useRouter()
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const token = localStorage.getItem('access')

    if (!token) {
      router.replace('/login')
    } else {
      setIsReady(true)
    }
  }, [router])

  return isReady
}
