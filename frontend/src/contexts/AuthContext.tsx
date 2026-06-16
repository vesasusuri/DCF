import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { User } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import type { AuthUser, UserRole } from '../types/auth'

type AuthContextValue = {
  user: AuthUser | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<AuthUser>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

function authUserFromSession(sessionUser: User): AuthUser {
  const metadata = sessionUser.user_metadata ?? {}
  const role: UserRole = metadata.role === 'admin' ? 'admin' : 'user'

  return {
    id: sessionUser.id,
    email: sessionUser.email ?? '',
    fullName:
      (typeof metadata.full_name === 'string' && metadata.full_name) ||
      sessionUser.email?.split('@')[0] ||
      'Benutzer',
    role,
  }
}

function resolveAuthUser(sessionUser: User): AuthUser {
  // Role lives in Supabase user_metadata (set by seed_admin script).
  // Avoids /rest/v1/profiles calls and broken RLS recursion on older migrations.
  return authUserFromSession(sessionUser)
}

export function formatAuthError(error: unknown): string {
  if (error && typeof error === 'object' && 'message' in error) {
    const message = String((error as { message: string }).message)

    if (message.toLowerCase().includes('invalid login credentials')) {
      return 'E-Mail oder Passwort ist falsch. Verwenden Sie die Demo-Zugänge unten.'
    }

    if (message.toLowerCase().includes('email not confirmed')) {
      return 'E-Mail-Adresse ist noch nicht bestätigt.'
    }

    return message
  }

  return 'Anmeldung fehlgeschlagen.'
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  const loadSession = useCallback(async () => {
    if (!supabase) {
      setUser(null)
      setLoading(false)
      return
    }

    const { data } = await supabase.auth.getSession()
    const sessionUser = data.session?.user

    if (!sessionUser) {
      setUser(null)
      setLoading(false)
      return
    }

    const profile = resolveAuthUser(sessionUser)
    setUser(profile)
    setLoading(false)
  }, [])

  useEffect(() => {
    void loadSession()

    if (!supabase) return

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session?.user) {
        setUser(null)
        setLoading(false)
        return
      }

      setUser(resolveAuthUser(session.user))
      setLoading(false)
    })

    return () => subscription.subscription.unsubscribe()
  }, [loadSession])

  const signIn = useCallback(async (email: string, password: string) => {
    if (!supabase) {
      throw new Error(
        'Supabase ist nicht konfiguriert. Setzen Sie VITE_SUPABASE_URL und VITE_SUPABASE_ANON_KEY und starten Sie die App neu.',
      )
    }

    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    if (!data.user) throw new Error('Anmeldung fehlgeschlagen.')

    const profile = resolveAuthUser(data.user)
    setUser(profile)
    return profile
  }, [])

  const signOut = useCallback(async () => {
    if (supabase) await supabase.auth.signOut()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      signIn,
      signOut,
    }),
    [user, loading, signIn, signOut],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export function getDefaultRouteForRole(role: UserRole) {
  return role === 'admin' ? '/admin' : '/projects'
}

export function getUserInitials(fullName: string) {
  const parts = fullName.trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return 'U'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
}
