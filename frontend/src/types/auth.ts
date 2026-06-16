export type UserRole = 'user' | 'admin'

export type AuthUser = {
  id: string
  email: string
  fullName: string
  role: UserRole
}

export type ProfileRow = {
  id: string
  email: string
  full_name: string | null
  role: UserRole
}
