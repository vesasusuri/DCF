export function useWebSocket(_url: string) {
  return {
    connected: false,
    lastMessage: null,
  }
}
