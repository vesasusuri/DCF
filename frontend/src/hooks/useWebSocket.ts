export function useWebSocket(url: string) {
  void url
  return {
    connected: false,
    lastMessage: null,
  }
}
