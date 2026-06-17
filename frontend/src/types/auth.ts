export type UserRole = 'user' | 'admin' | 'portfolio_manager'

export type OnboardingStep = 'change-password' | 'verify-email' | 'complete'

export type AuthUser = {
  id: string
  email: string
  fullName: string
  role: UserRole
  onboardingStep: OnboardingStep
}

export type ProfileRow = {
  id: string
  email: string
  full_name: string | null
  role: UserRole
}
