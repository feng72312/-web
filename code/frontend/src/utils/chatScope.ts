export function isScopeRefusalMessage(message: string): boolean {
  const text = message.trim();
  return (
    text.includes("本助手仅解答预测") ||
    text.includes("本助手仅解答命理") ||
    text.includes("请围绕问事") ||
    text.includes("请围绕你的具体问题")
  );
}
