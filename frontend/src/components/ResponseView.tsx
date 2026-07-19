export function ResponseView({ text }: { text: string }) {
  return <section><p className="eyebrow">AI</p><p className={text ? "message" : "placeholder"}>{text || "回答がここに表示されます"}</p></section>;
}
