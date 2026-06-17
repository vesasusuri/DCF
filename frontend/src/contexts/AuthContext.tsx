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
import { recordPlatformEvent } from '../lib/audit'
import { getOnboardingStep } from '../lib/onboarding'
import type { AuthUser, UserRole } from '../types/auth'

type AuthContextValue = {
  user: AuthUser | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<AuthUser>
  signOut: () => Promise<void>
  changePassword: (newPassword: string) => Promise<AuthUser>
  resendVerificationEmail: () => Promise<void>
  refreshUser: () => Promise<AuthUser | null>
}

const AuthContext = createContext<AuthContextValue | null>(null)

function authUserFromSession(sessionUser: User): AuthUser {
  const metadata = sessionUser.user_metadata ?? {}
  function normalizeRole(metadataRole: unknown): UserRole {
    if (metadataRole === 'admin') return 'admin'
    if (metadataRole === 'portfolio_manager' || metadataRole === 'PORTFOLIO_MANAGER') {
      return 'portfolio_manager'
    }
    return 'user'
  }
  const role = normalizeRole(metadata.role)

  return {
    id: sessionUser.id,
    email: sessionUser.email ?? '',
    fullName:
      (typeof metadata.full_name === 'string' && metadata.full_name) ||
      sessionUser.email?.split('@')[0] ||
      'Benutzer',
    role,
    onboardingStep: getOnboardingStep(sessionUser),
  }
}

function resolveAuthUser(sessionUser: User): AuthUser {
  return authUserFromSession(sessionUser)
}

export function formatAuthError(error: unknown): string {
  if (error && typeof error === 'object' && 'message' in error) {
    const message = String((error as { message: string }).message)

    if (message.toLowerCase().includes('invalid login credentials')) {
      return 'E-Mail oder Passwort ist falsch.'
    }

    if (message.toLowerCase().includes('email not confirmed')) {
      return 'Bitte bestätigen Sie zuerst Ihre E-Mail-Adresse.'
    }

    return message
  }

  return 'Anmeldung fehlgeschlagen.'
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  const applySession = useCallback((sessionUser: User | null) => {
    if (!sessionUser) {
      setUser(null)
      return null
    }
    const profile = resolveAuthUser(sessionUser)
    setUser(profile)
    return profile
  }, [])

  const refreshUser = useCallback(async () => {
    if (!supabase) {
      setUser(null)
      return null
    }

    const { data, error } = await supabase.auth.refreshSession()
    if (error || !data.session?.user) {
      setUser(null)
      return null
    }

    return applySession(data.session.user)
  }, [applySession])

  const loadSession = useCallback(async () => {
    if (!supabase) {
      setUser(null)
      setLoading(false)
      return
    }

    const { data } = await supabase.auth.getSession()
    applySession(data.session?.user ?? null)
    setLoading(false)
  }, [applySession])

  useEffect(() => {
    void loadSession()

    if (!supabase) return

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, session) => {
      applySession(session?.user ?? null)
      setLoading(false)
    })

    return () => subscription.subscription.unsubscribe()
  }, [applySession, loadSession])

  const signIn = useCallback(async (email: string, password: string) => {
    if (!supabase) {
      throw new Error(
        'Supabase ist nicht konfiguriert. Setzen Sie VITE_SUPABASE_URL und VITE_SUPABASE_ANON_KEY.',
      )
    }

    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    if (!data.user) throw new Error('Anmeldung fehlgeschlagen.')

    const profile = applySession(data.user)!
    void recordPlatformEvent({ action: 'login' })
    return profile
  }, [applySession])

  const changePassword = useCallback(async (newPassword: string) => {
    if (!supabase) throw new Error('Supabase ist nicht konfiguriert.')

    const { data, error } = await supabase.auth.updateUser({
      password: newPassword,
      data: { must_change_password: false },
    })
    if (error) throw error
    if (!data.user) throw new Error('Passwort konnte nicht geändert werden.')

    const email = data.user.email
    if (email) {
      await supabase.auth.resend({ type: 'signup', email })
    }

    return applySession(data.user)!
  }, [applySession])

  const resendVerificationEmail = useCallback(async () => {
    if (!supabase || !user?.email) throw new Error('Keine Sitzung gefunden.')
    const { error } = await supabase.auth.resend({ type: 'signup', email: user.email })
    if (error) throw error
  }, [user?.email])

  const signOut = useCallback(async () => {
    if (user) {
      void recordPlatformEvent({ action: 'logout' })
    }
    if (supabase) await supabase.auth.signOut()
    setUser(null)
  }, [user])

  const value = useMemo(
    () => ({
      user,
      loading,
      signIn,
      signOut,
      changePassword,
      resendVerificationEmail,
      refreshUser,
    }),
    [user, loading, signIn, signOut, changePassword, resendVerificationEmail, refreshUser],
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
