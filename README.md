# LiveLLM

ローカルでSTTとTTSを処理し、外部のOpenAI互換LLMへ文字列だけを送るリアルタイム音声対話MVPです。

## Requirements

- Apple Silicon Mac
- Docker Desktop with Compose
- Node.js 22+
- Python 3.12+ and `uv`
- Chrome最新版

## Setup

```sh
./scripts/setup.sh
```

生成された`.env`へ`LLM_API_KEY`と`LLM_MODEL`を設定します。互換APIを使う場合は`LLM_BASE_URL`も変更してください。

## LLM接続先の設定例

GatewayはOpenAI互換の`POST /chat/completions`を使用するため、LM StudioとOpenRouterのどちらにも接続できます。設定変更後はGatewayを再起動してください。

### LM Studio

1. LM Studioでチャット対応モデルをダウンロードしてロードします。
2. Developer画面からLocal Serverを開始します（CLIでは`lms server start`）。
3. Docker内のGatewayから接続できるよう、必要に応じてLM Studioの`Serve on Local Network`を有効にします。
4. ルートの`.env`を次のように設定します。

```env
LLM_BASE_URL=http://host.docker.internal:1234/v1
LLM_API_KEY=lm-studio
LLM_MODEL=LM Studioに表示されるモデル識別子
```

`localhost`ではなく`host.docker.internal`を使うのは、GatewayがDockerコンテナ内で動作するためです。LM StudioのOpenAI互換APIは既定で`http://localhost:1234/v1`と`/v1/chat/completions`を提供します。認証を有効にした場合は、`LLM_API_KEY`へLM Studioで発行したAPIトークンを設定してください。

参考: [LM Studio OpenAI Compatibility](https://lmstudio.ai/docs/developer/openai-compat/chat-completions)

### OpenRouter

1. OpenRouterでAPIキーを発行します。
2. 利用するモデルのslugをモデル一覧で確認します。
3. ルートの`.env`を次のように設定します。

```env
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
LLM_MODEL=anthropic/claude-haiku-4.5
```

モデル名には`provider/model-name`形式のOpenRouter slugを指定します。上記モデルは設定例なので、実際に利用可能で目的に合うモデルへ置き換えてください。APIキーは`.env`だけに保存し、Gitへコミットしないでください。

参考: [OpenRouter Quickstart](https://openrouter.ai/docs/quickstart)、[OpenRouter Authentication](https://openrouter.ai/docs/api/reference/authentication)

設定反映後、Gatewayだけを再作成できます。

```sh
docker compose up -d --force-recreate gateway
```

## Start

```sh
./scripts/start-dev.sh
cd frontend
npm run dev
```

初回はwhisper.cppのビルド、モデルとVOICEVOXイメージの取得に時間がかかります。`http://127.0.0.1:5173`をChromeで開いてください。

## Test

```sh
./scripts/test.sh
./scripts/smoke-test.sh
```

手動の確認項目は[docs/verification.md](docs/verification.md)、通信仕様は[docs/websocket-protocol.md](docs/websocket-protocol.md)を参照してください。

後続実装の課題は[TODO.md](TODO.md)を参照してください。

## Stop

```sh
./scripts/stop-dev.sh
```

秘密値を含む`.env`はGit管理対象外です。ブラウザへ渡るのは`frontend/.env`の`VITE_*`値だけです。
