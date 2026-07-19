export function TranscriptView({ text }: { text: string }) {
  return <section><p className="eyebrow">あなた</p><p className={text ? "message" : "placeholder"}>{text || "発話内容がここに表示されます"}</p></section>;
}
