# リアルタイム音声対話Webアプリ 実装方針

## 1. 目的

GPT Liveのように、ブラウザから音声で会話できるリアルタイム音声対話アプリを構築する。

本システムでは以下を実現する。

- ブラウザのマイクから音声を取得する
- 音声をローカル環境で文字起こしする
- 文字列を外部LLM APIへ送信する
- LLMの応答をローカル環境で音声合成する
- ブラウザで応答音声を再生する
- 将来的にストリーミング、割り込み、途中字幕へ拡張できる構造にする

外部へ送信するのは原則として文字起こし後のテキストのみとし、マイク音声は外部LLMへ送信しない。

---

## 2. 採用構成

```text
Webブラウザ
    │
    │ WebSocket
    │ PCM音声 / 制御イベント
    ▼
Voice Gateway
    ├─ STT：whisper.cpp（ローカル）
    ├─ LLM：外部API
    └─ TTS：VOICEVOX Engine（ローカル）
```

### コンポーネント

| 区分 | 採用技術 |
|---|---|
| Webフロントエンド | React + TypeScript + Vite |
| マイク入力 | Web Audio API + AudioWorklet |
| 通信 | WebSocket |
| Gateway | Python + FastAPI |
| VAD | Silero VAD |
| STT | whisper.cpp |
| LLM | 外部API |
| TTS | VOICEVOX Engine |
| 設定管理 | `.env` |
| 会話履歴 | 初期版はメモリ保持 |
| 永続化 | 初期版では不要 |

---

## 3. 基本方針

### 3.1 各機能を疎結合にする

STT、LLM、TTSは個別のクライアントクラスとして実装する。

```text
VoiceSession
├─ SttClient
├─ LlmClient
├─ TtsClient
├─ VadProcessor
└─ SentenceSegmenter
```

各実装はインターフェースを介して利用する。

目的は以下。

- モデルやサービスを後から差し替えられる
- 単体テストしやすくする
- 外部API固有の処理をGateway全体へ拡散させない
- ローカルLLMへの切り替えも可能にする

---

### 3.2 初期版は単純な一往復を優先する

最初から完全リアルタイム処理を実装しない。

最初のMVPでは以下を完成させる。

```text
録音開始
  ↓
録音停止
  ↓
whisper.cppで文字起こし
  ↓
外部LLMへ送信
  ↓
回答全文を取得
  ↓
VOICEVOXで音声生成
  ↓
ブラウザで再生
```

この一連の処理が安定した後、段階的にリアルタイム化する。

---

## 4. システム構成

## 4.1 Webフロントエンド

### 責務

- マイク利用許可
- 音声録音
- PCMへの変換
- WebSocket接続
- 音声データ送信
- 文字起こし結果の表示
- LLM応答テキストの表示
- 合成音声の再生
- 状態表示
- 再生停止
- エラー表示

### 推奨画面

```text
┌─────────────────────────────┐
│ 接続状態                    │
│                             │
│ ユーザー発話                │
│                             │
│ AI応答                      │
│                             │
│ [録音開始 / 録音停止]       │
│ [会話リセット]              │
└─────────────────────────────┘
```

### 状態

```typescript
type VoiceAppState =
  | "disconnected"
  | "idle"
  | "listening"
  | "transcribing"
  | "thinking"
  | "synthesizing"
  | "speaking"
  | "error";
```

---

## 4.2 Voice Gateway

### 責務

- WebSocket接続管理
- 音声チャンク受信
- 音声バッファ管理
- 発話開始・終了管理
- whisper.cpp呼び出し
- LLM API呼び出し
- VOICEVOX呼び出し
- セッション管理
- 会話履歴管理
- キャンセル制御
- エラーのクライアント通知

### セッションモデル

```python
class VoiceSession:
    session_id: str
    state: str
    audio_buffer: bytearray
    messages: list[dict[str, str]]
    current_transcript: str
    current_response: str
```

初期版では、1 WebSocket接続につき1セッションとする。

---

## 4.3 STT

### 採用

`whisper.cpp`

### 実行方法

whisper.cppはGatewayとは別プロセスとしてHTTPサーバーで起動する。

```text
Voice Gateway
    │ HTTP
    ▼
whisper.cpp server
```

### 方針

- 音声はローカル処理する
- 外部APIへ音声を送らない
- モデルは設定ファイルで変更可能にする
- 日本語中心で利用する
- 初期版では録音終了後にまとめて文字起こしする
- 将来は途中認識へ拡張する

### 推奨モデル

初期値は以下のどちらかとする。

```text
small
medium
```

低スペック環境では`small`を初期値とする。

### STTクライアント

```python
class SttClient:
    async def transcribe(self, audio_data: bytes) -> str:
        ...
```

---

## 4.4 LLM

### 採用

外部LLM APIを利用する。

### 必須要件

- ストリーミング応答対応
- 日本語対応
- 最初のトークンが速い
- OpenAI互換APIを優先
- APIキーを環境変数で管理
- モデル名を環境変数で変更可能
- タイムアウトを設定
- キャンセル可能な構造にする

### 初期版

初期版ではストリーミングを使わず、回答全文を取得してもよい。

第2段階でストリーミングへ変更する。

### LLMクライアント

```python
class LlmClient:
    async def complete(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        ...

    async def stream(
        self,
        messages: list[dict[str, str]],
    ):
        ...
```

### システムプロンプト

```text
あなたはリアルタイム音声会話用のアシスタントです。

- 日本語で回答してください
- 回答は簡潔にしてください
- 原則として2〜4文以内で回答してください
- 音声で聞き取りやすい自然な文にしてください
- Markdownの表や複雑な箇条書きは避けてください
- URLやコードを長く読み上げないでください
- 不明な点は推測せず、その旨を簡潔に伝えてください
```

---

## 4.5 TTS

### 採用

`VOICEVOX Engine`

### 実行方法

VOICEVOX EngineをローカルHTTPサーバーとして起動する。

```text
Voice Gateway
    │ HTTP
    ▼
VOICEVOX Engine
```

### 処理手順

```text
テキスト
  ↓
audio_query
  ↓
synthesis
  ↓
WAV
```

### TTSクライアント

```python
class TtsClient:
    async def synthesize(
        self,
        text: str,
        speaker_id: int,
    ) -> bytes:
        ...
```

### 方針

- speaker_idは環境変数で指定
- 音声速度なども設定可能にする
- 初期版では回答全文を一度に音声化
- 第2段階で文単位の逐次音声化へ変更する

---

## 5. WebSocket設計

## 5.1 クライアントからサーバー

### セッション開始

```json
{
  "type": "session.start"
}
```

### 録音開始

```json
{
  "type": "input.start"
}
```

### 音声データ

音声データはWebSocketのバイナリフレームで送信する。

JSONへBase64エンコードしない。

### 録音終了

```json
{
  "type": "input.commit"
}
```

### 応答キャンセル

```json
{
  "type": "response.cancel"
}
```

### 会話リセット

```json
{
  "type": "session.reset"
}
```

---

## 5.2 サーバーからクライアント

### 状態変更

```json
{
  "type": "session.state",
  "state": "transcribing"
}
```

### 文字起こし結果

```json
{
  "type": "transcript.final",
  "text": "今日の天気を教えてください"
}
```

### LLM応答

```json
{
  "type": "response.text.final",
  "text": "今日は晴れる見込みです。"
}
```

### 音声生成開始

```json
{
  "type": "response.audio.started"
}
```

### 音声データ

WAVまたはPCMをバイナリフレームで返す。

### 応答完了

```json
{
  "type": "response.completed"
}
```

### エラー

```json
{
  "type": "error",
  "code": "STT_FAILED",
  "message": "音声認識に失敗しました"
}
```

---

## 6. 音声形式

ブラウザからGatewayへ送る音声形式は以下へ統一する。

```text
PCM
16,000 Hz
16-bit signed integer
mono
little endian
```

### Web側

```text
MediaStream
  ↓
AudioContext
  ↓
AudioWorklet
  ↓
Float32
  ↓
16kHzへリサンプリング
  ↓
Int16 PCM
  ↓
WebSocket
```

### 注意点

- `MediaRecorder`は原則使用しない
- ブラウザ依存の圧縮形式を避ける
- 音声チャンクは20〜100ms程度を目安にする
- Base64変換は行わない

---

## 7. ディレクトリ構成

```text
realtime-voice-app/
├─ frontend/
│  ├─ src/
│  │  ├─ audio/
│  │  │  ├─ recorder-worklet.ts
│  │  │  ├─ audio-recorder.ts
│  │  │  ├─ audio-player.ts
│  │  │  └─ pcm-converter.ts
│  │  ├─ websocket/
│  │  │  ├─ voice-socket.ts
│  │  │  └─ events.ts
│  │  ├─ components/
│  │  │  ├─ VoiceControl.tsx
│  │  │  ├─ TranscriptView.tsx
│  │  │  ├─ ResponseView.tsx
│  │  │  └─ StatusIndicator.tsx
│  │  ├─ hooks/
│  │  │  └─ useVoiceSession.ts
│  │  ├─ App.tsx
│  │  └─ main.tsx
│  ├─ public/
│  │  └─ recorder-worklet.js
│  └─ package.json
│
├─ gateway/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ config.py
│  │  ├─ websocket_endpoint.py
│  │  ├─ session.py
│  │  ├─ event_models.py
│  │  ├─ clients/
│  │  │  ├─ stt_client.py
│  │  │  ├─ llm_client.py
│  │  │  └─ tts_client.py
│  │  ├─ audio/
│  │  │  ├─ buffer.py
│  │  │  ├─ wav.py
│  │  │  └─ vad.py
│  │  └─ services/
│  │     ├─ conversation_service.py
│  │     └─ sentence_segmenter.py
│  ├─ tests/
│  └─ pyproject.toml
│
├─ scripts/
│  ├─ start-whisper.sh
│  ├─ start-voicevox.sh
│  └─ start-dev.sh
│
├─ .env.example
├─ docker-compose.yml
├─ README.md
└─ IMPLEMENTATION_POLICY.md
```

---

## 8. 環境変数

```env
APP_HOST=0.0.0.0
APP_PORT=8000

STT_BASE_URL=http://localhost:8080
STT_MODEL=small
STT_LANGUAGE=ja
STT_TIMEOUT_SECONDS=60

LLM_BASE_URL=https://example.com/v1
LLM_API_KEY=
LLM_MODEL=
LLM_TIMEOUT_SECONDS=60
LLM_TEMPERATURE=0.6
LLM_MAX_TOKENS=256

TTS_BASE_URL=http://localhost:50021
TTS_SPEAKER_ID=1
TTS_TIMEOUT_SECONDS=60

MAX_AUDIO_SECONDS=60
MAX_HISTORY_MESSAGES=20
LOG_LEVEL=INFO
```

秘密情報をGitへコミットしない。

`.env.example`にはキー名だけを記載し、実際のAPIキーは含めない。

---

## 9. 実装フェーズ

## フェーズ1：MVP

以下を完成させる。

- React画面
- WebSocket接続
- 録音開始・停止
- PCM送信
- whisper.cppによる文字起こし
- 外部LLMへの問い合わせ
- VOICEVOXによる音声合成
- ブラウザで音声再生
- エラー表示
- 会話履歴のメモリ保持

### 完了条件

1回の発話に対して、以下が成立すること。

```text
音声入力
  ↓
文字起こし表示
  ↓
AI回答表示
  ↓
AI音声再生
```

---

## フェーズ2：低遅延化

以下を追加する。

- LLMストリーミング
- 応答テキストの逐次表示
- 文単位でのTTS生成
- TTS再生キュー
- 最初の音声再生までの時間短縮

### 文分割ルール

以下を文の区切りとして扱う。

```text
。
！
？
\n
```

短すぎる断片は直ちにTTSへ送らず、一定文字数までバッファする。

---

## フェーズ3：リアルタイム会話

以下を追加する。

- Silero VAD
- 発話開始検出
- 発話終了検出
- 音声再生中の割り込み
- LLM生成キャンセル
- TTS生成キャンセル
- ブラウザ再生キュー停止

### 状態遷移

```text
IDLE
  ↓
LISTENING
  ↓
TRANSCRIBING
  ↓
THINKING
  ↓
SYNTHESIZING
  ↓
SPEAKING
```

割り込み時は以下。

```text
SPEAKING
  ↓
INTERRUPTED
  ↓
LISTENING
```

---

## フェーズ4：品質改善

必要に応じて追加する。

- STT途中字幕
- ノイズ抑制
- エコー対策
- 会話履歴要約
- 長時間セッション対応
- RAG
- Function Calling
- ツール実行
- 設定画面
- speaker_id選択
- モデル選択
- API使用量表示

---

## 10. キャンセル設計

すべての長時間処理はキャンセル可能にする。

対象。

- STT
- LLM
- TTS
- 音声再生

Pythonでは`asyncio.Task`を保持し、キャンセル時に`cancel()`する。

```python
session.llm_task.cancel()
session.tts_task.cancel()
```

Webクライアントでは以下を停止する。

- 現在再生中のAudioBufferSourceNode
- 再生待ちキュー
- 不要になったレスポンスの処理

---

## 11. エラー処理

エラーコードを明示的に定義する。

```text
INVALID_EVENT
INVALID_AUDIO_FORMAT
AUDIO_TOO_LONG
STT_UNAVAILABLE
STT_FAILED
LLM_UNAVAILABLE
LLM_FAILED
TTS_UNAVAILABLE
TTS_FAILED
SESSION_NOT_FOUND
INTERNAL_ERROR
```

### 方針

- 内部例外をそのままクライアントへ返さない
- ログには詳細を記録する
- クライアントには安全なメッセージを返す
- 外部APIのレスポンス本文に秘密情報が含まれないよう注意する
- タイムアウトを必ず設定する

---

## 12. ログ

ログへ以下を記録する。

- session_id
- 処理種別
- 処理開始時刻
- 処理終了時刻
- 処理時間
- 音声秒数
- 文字起こし文字数
- LLM応答文字数
- エラー種別

原則として、音声バイナリやAPIキーはログへ記録しない。

会話本文のログ保存は設定で有効・無効を切り替えられるようにする。

---

## 13. セキュリティ

最低限、以下を実装する。

- APIキーをフロントエンドへ渡さない
- LLM API呼び出しは必ずGateway経由
- `.env`をGit管理対象外にする
- WebSocketの受信サイズを制限する
- 音声時間を制限する
- CORSを必要最小限にする
- 本番環境ではHTTPS/WSSを使用する
- 外部LLMへ送る内容を明示する
- 機密情報を扱う場合はマスキング機構を検討する

---

## 14. テスト方針

## 14.1 単体テスト

対象。

- PCM変換
- WAV生成
- 文分割
- WebSocketイベント解析
- 会話履歴管理
- APIレスポンス変換
- エラー変換

## 14.2 モック

STT、LLM、TTSクライアントはモック可能にする。

```python
class FakeSttClient:
    async def transcribe(self, audio_data: bytes) -> str:
        return "テスト音声です"
```

外部サービスなしでGatewayのテストを実行可能にする。

## 14.3 結合テスト

最低限、以下を確認する。

- whisper.cpp接続
- LLM API接続
- VOICEVOX接続
- WebSocket一往復
- エラー時のクライアント通知

---

## 15. 非機能要件

### 初期目標

| 項目 | 目標 |
|---|---|
| 最大録音時間 | 60秒 |
| 同時接続 | 1〜5セッション |
| STT言語 | 日本語 |
| LLM回答 | 原則2〜4文 |
| 初期応答時間 | 5秒以内を目標 |
| エラー時 | UI上に明示 |
| APIキー | サーバー側のみ保持 |

### 第2段階以降

| 項目 | 目標 |
|---|---|
| 発話終了から最初の音声 | 2秒以内 |
| LLMストリーミング | 必須 |
| 音声割り込み | 対応 |
| STT途中字幕 | 対応検討 |

---

## 16. Codexへの実装指示

以下の順序で実装すること。

1. プロジェクト雛形を作成する
2. `.env.example`を作成する
3. Gatewayの設定管理を実装する
4. WebSocketイベントモデルを定義する
5. フロントエンドで録音とPCM送信を実装する
6. Gatewayで音声バッファを受信する
7. whisper.cppクライアントを実装する
8. LLMクライアントを実装する
9. VOICEVOXクライアントを実装する
10. 一連の会話フローを実装する
11. 音声再生を実装する
12. エラー処理を実装する
13. モックを用いたテストを追加する
14. READMEへ起動方法を記載する
15. MVP完了後にストリーミング対応へ進む

一度にすべてを実装せず、各段階で動作確認可能な状態を維持すること。

---

## 17. Codex向け制約

- 不明点を独自判断で大きく変更しない
- STTとTTSを外部APIへ置き換えない
- 音声を外部LLMへ直接送信しない
- APIキーをソースコードへ記載しない
- フロントエンドから外部LLM APIを直接呼び出さない
- Base64音声通信を採用しない
- 初期版で過剰な永続化や認証機構を追加しない
- 依存ライブラリを必要以上に増やさない
- 各クライアントの責務を分離する
- 非同期処理にはタイムアウトとキャンセルを設ける
- 実装後に起動手順と検証手順をREADMEへ記載する

---

## 18. 最終的な完了条件

以下を満たした時点でMVP完了とする。

- ブラウザからマイク録音できる
- 音声がGatewayへ送信される
- whisper.cppで日本語文字起こしできる
- 文字起こし結果が画面へ表示される
- 外部LLMから日本語応答を取得できる
- 応答テキストが画面へ表示される
- VOICEVOXで音声を生成できる
- ブラウザでAI音声を再生できる
- APIキーがフロントエンドへ露出しない
- エラー時に画面へ内容が表示される
- READMEの手順だけでローカル起動できる
