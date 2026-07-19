import "./App.css";
import { ErrorMessage } from "./components/ErrorMessage";
import { ResponseView } from "./components/ResponseView";
import { StatusIndicator } from "./components/StatusIndicator";
import { TranscriptView } from "./components/TranscriptView";
import { VoiceControl } from "./components/VoiceControl";
import { useVoiceSession } from "./session/useVoiceSession";

export default function App() {
  const { view, connect, startRecording, stopRecording, cancel, reset } = useVoiceSession();
  return <main>
    <div className="shell">
      <header><div><p className="kicker">LIVE LLM</p><h1>声で、自然に話そう。</h1></div><StatusIndicator state={view.state} /></header>
      <div className="conversation"><TranscriptView text={view.transcript} /><ResponseView text={view.response} /></div>
      <ErrorMessage message={view.error} />
      <VoiceControl state={view.state} onStart={() => void startRecording()} onStop={() => void stopRecording()} onCancel={cancel} onReset={reset} onReconnect={() => void connect()} />
      <p className="hint">話し終えて約1.2秒待つと、自動で回答を始めます。</p>
    </div>
  </main>;
}
