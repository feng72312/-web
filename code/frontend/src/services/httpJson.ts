export async function parseResponseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  const trimmed = text.trim();
  if (trimmed.startsWith("<")) {
    throw new Error(
      "后端返回了网页而非数据, 请按 Ctrl+F5 强刷页面后重试",
    );
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error(trimmed.slice(0, 160) || "响应解析失败");
  }
}
