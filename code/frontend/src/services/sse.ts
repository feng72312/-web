export async function readSseStream<T>(
  response: Response,
  onEvent: (payload: T) => void,
): Promise<void> {
  if (!response.body) {
    throw new Error("empty response body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";

    for (const part of parts) {
      const line = part.split("\n").find((item) => item.startsWith("data: "));
      if (!line) {
        continue;
      }
      onEvent(JSON.parse(line.slice(6)) as T);
    }
  }
}
