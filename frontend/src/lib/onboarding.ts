import type { User } from '@supabase/supabase-js'
import type { OnboardingStep, UserRole } from '../types/auth'

export function mustChangePassword(user: User | null | undefined): boolean {
  if (!user) return false
  return Boolean(user.user_metadata?.must_change_password)
}

export function isEmailVerified(user: User | null | undefined): boolean {
  if (!user) return false
  const metadata = user.user_metadata ?? {}
  if (metadata.invited === true) {
    return metadata.email_verified === true
  }
  return Boolean(user.email_confirmed_at)
}

export function getOnboardingStep(user: User | null | undefined): OnboardingStep {
  if (!user) return 'complete'
  if (mustChangePassword(user)) return 'change-password'
  if (!isEmailVerified(user)) return 'verify-email'
  return 'complete'
}

export function getOnboardingPath(user: User | null | undefined): string | null {
  const step = getOnboardingStep(user)
  if (step === 'change-password') return '/auth/change-password'
  if (step === 'verify-email') return '/auth/verify-email'
  return null
}

export function getPostAuthPath(profile: {
  role: UserRole
  onboardingStep: OnboardingStep
}): string {
  if (profile.onboardingStep === 'change-password') return '/auth/change-password'
  if (profile.onboardingStep === 'verify-email') return '/auth/verify-email'
  if (profile.role === 'admin') return '/admin'
  return '/projects'
}
